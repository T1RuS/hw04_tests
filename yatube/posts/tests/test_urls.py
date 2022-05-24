from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from ..models import Group, Post


User = get_user_model()


class StaticURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            group=cls.group,
            author=cls.author,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client_user = Client()
        self.authorized_client_author = Client()
        self.authorized_client_user.force_login(self.user)
        self.authorized_client_author.force_login(StaticURLTests.author)

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test_group/',
            'posts/profile.html': '/profile/author/',
            'posts/post_detail.html': '/posts/1/',
        }

        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

        response = self.authorized_client_user.get('/create/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

        response = self.authorized_client_author.get('/posts/1/edit/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_urls_uses_correct_redirect(self):
        response = self.authorized_client_user.get('/posts/1/edit/')
        self.assertRedirects(response, '/posts/1/')

        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_urls_uses_correct_status(self):
        list_urls = ['/posts/1/', '/profile/author/', '/group/test_group/', '/']
        for url in list_urls:
            response = self.guest_client.get(url)
            self.assertEqual(response.status_code, 200)

        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, 302)

        response = self.authorized_client_user.get('/posts/1/edit/')
        self.assertEqual(response.status_code, 302)

        response = self.authorized_client_author.get('/posts/1/edit/')
        self.assertEqual(response.status_code, 200)

        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

