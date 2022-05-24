import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Post, Group


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание'
        )

        Post.objects.create(
            text='Тестовый пост',
            group=cls.group,
            author=cls.author,
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(CreateFormTests.author)

    def test_create_post(self):
        tasks_count = Post.objects.count()

        form_data = {
            'text': 'Тестовый пост2',
            'author': CreateFormTests.author,
        }

        response = self.authorized_client_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertEqual(Post.objects.count(), tasks_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост2',
                author=CreateFormTests.author,
            ).exists()
        )

        self.assertRedirects(response,
                             reverse('posts:profile', args=['author']))

    def test_create_edit_post(self):
        form_data = {
            'text': 'Новый текст',
            'author': CreateFormTests.author,
        }

        response = self.authorized_client_author.post(
            reverse('posts:post_edit', args=[1]),
            data=form_data,
            follow=True
        )

        self.assertTrue(
            Post.objects.filter(
                text='Новый текст',
                author=CreateFormTests.author,
            ).exists()
        )

        self.assertRedirects(response,
                             reverse('posts:post_detail', args=[1]))
