from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django import forms

from ..models import Group, Post


User = get_user_model()


class StaticViewsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание'
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test_group2',
            description='Тестовое описание2'
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
        self.authorized_client_author.force_login(StaticViewsTests.author)

    def test_views_uses_correct_template(self):
        response = self.guest_client.get(reverse('posts:index'))
        self.assertTemplateUsed((response, 'posts/index.html'))

        response = self.guest_client.get(
            reverse('posts:group_list', args=['test_group']))
        self.assertTemplateUsed((response, 'posts/group_list.html'))

        response = self.guest_client.get(
            reverse('posts:profile', args=['author']))
        self.assertTemplateUsed((response, 'posts/profile.html'))

        response = self.guest_client.get(
            reverse('posts:post_detail', args=[1]))
        self.assertTemplateUsed((response, 'posts/post_detail.html'))

        response = self.authorized_client_user.get(
            reverse('posts:post_create'))
        self.assertTemplateUsed(response, 'posts/create_post.html')

        response = self.authorized_client_author.get(
            reverse('posts:post_edit', args=[1]))
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_views_uses_context_index_page(self):
        response = self.client.get(reverse('posts:index'))

        post = StaticViewsTests.post
        response_post = response.context.get('page_obj')[0]
        self.assertEqual(response_post.author, post.author)
        self.assertEqual(response_post.group, post.group)
        self.assertEqual(response_post.text, post.text)

    def test_views_uses_context_group_list_page(self):
        response = self.client.get(
            reverse('posts:group_list', args=['test_group']))

        post = StaticViewsTests.post
        response_post = response.context.get('page_obj')[0]
        self.assertEqual(response_post.author, post.author)
        self.assertEqual(response_post.group, post.group)
        self.assertEqual(response_post.text, post.text)

    def test_views_uses_context_profile_page(self):
        response = self.client.get(reverse('posts:profile', args=['author']))

        post = StaticViewsTests.post
        response_post = response.context.get('page_obj')[0]
        self.assertEqual(response_post.author, post.author)
        self.assertEqual(response_post.group, post.group)
        self.assertEqual(response_post.text, post.text)

        response_post = response.context.get('author')
        self.assertEqual(response_post, post.author)

        response_post = response.context.get('count_posts')
        self.assertEqual(response_post, 1)

    def test_views_uses_context_post_detail_page(self):
        response = self.client.get(reverse('posts:post_detail', args=[1]))

        post = StaticViewsTests.post
        response_post = response.context.get('post')
        self.assertEqual(response_post.author, post.author)
        self.assertEqual(response_post.group, post.group)
        self.assertEqual(response_post.text, post.text)

        response_post = response.context.get('name_post')
        self.assertEqual(response_post, post.text)

        response_post = response.context.get('count_posts')
        self.assertEqual(response_post, 1)

    def test_views_uses_context_post_edit_page(self):
        response = self.authorized_client_author.get(
            reverse('posts:post_edit', args=[1]))

        response_post = response.context.get('title')
        self.assertEqual(response_post, 'Изменение поста')

        response_post = response.context.get('is_edit')
        self.assertEqual(response_post, True)

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_views_uses_context_post_create_page(self):
        response = self.authorized_client_author.get(
            reverse('posts:post_create'))

        response_post = response.context.get('title')
        self.assertEqual(response_post, 'Создание поста')

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_views_uses_context_post_create(self):
        self.post = Post.objects.create(
            text='Тестовый пост2',
            group=StaticViewsTests.group2,
            author=self.user,
        )

        response = self.guest_client.get(reverse('posts:index'))
        response_post = response.context.get('page_obj')[0]

        self.assertEqual(response_post.pk, self.post.pk)

        response = self.guest_client.get(
            reverse('posts:group_list', args=['test_group2']))
        response_post = response.context.get('page_obj')

        for post in response_post:
            with self.subTest(value=post):
                self.assertEqual(post.group, self.post.group)

        response = self.guest_client.get(
            reverse('posts:profile', args=['HasNoName']))
        response_post = response.context.get('page_obj')
        for post in response_post:
            with self.subTest(value=post):
                self.assertEqual(post.author, self.post.author)

        response = self.guest_client.get(
            reverse('posts:group_list', args=['test_group']))
        response_post = response.context.get('page_obj')
        for post in response_post:
            with self.subTest(value=post):
                self.assertNotEqual(post.group, self.post.group)
