from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Post

class PostModelTest(TestCase):

    def setUp(self):
        """создание тестовых данных перед запуском тестов."""
        self.user = User.objects.create_user(
            username='testuser', password='password123'
        )

        self.draft_post = Post.objects.create(
            title='Черновик',
            slug='draft-post',
            author=self.user,
            body='Текст черновика',
            status=Post.Status.DRAFT,
        )

        self.published_post = Post.objects.create(
            title='Статья',
            slug='published-post',
            author=self.user,
            body='Текст статьи',
            status=Post.Status.PUBLISHED,
        )

    def test_published_manager_returns_only_published_posts(self):
        """Проверяем PublishManager - возврат опубликованных постов"""
        published_posts = Post.published.all()

        self.assertIn(self.published_post, published_posts)

        self.assertNotIn(self.draft_post, published_posts)

        self.assertEqual(published_posts.count(), 1)


    def test_post_list_view_does_not_contain_draft(self):
        """Проверяем опубликованные посты на главной странице"""
        response = self.client.get(reverse('blog:post_list'))

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self.published_post.title)

        self.assertNotContains(response, self.draft_post.title)