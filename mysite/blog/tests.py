from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.core import mail

from .models import Post

class PostModelTest(TestCase):

    def setUp(self):
        """Создаем тестовых данных перед запуском тестов."""
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


    def test_posts_share_sends_mail(self):
        """Проверяем успешную валидацию формы и отправку через outbox"""
        url = reverse('blog:post_share', args=[self.published_post.id])
        response = self.client.post(url, {
            'name': 'Катя',
            'email': 'sender@example.com',
            'to': 'receiver@example.com',
            'comments': 'Прочитай это!'
        })

        self.assertIn(response.status_code, [200, 302])

        self.assertEqual(len(mail.outbox), 1)

        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.to, ['receiver@example.com'])
        self.assertIn('Катя', sent_email.subject)


    def test_search_posts(self):
        """Проверяем успешную работу поиска статей"""
        url = reverse('blog:post_search')
        response = self.client.get(url, {
            'query': 'Published',
        })

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self.published_post.title)

        self.assertNotContains(response, self.draft_post.title)


    def test_post_comment(self):
        """Проверяем успешную работу добавления комментариев"""
        url = reverse('blog:post_comment', args=[self.published_post.id])
        response = self.client.post(url, {
            'name': 'Вова',
            'email': 'sender@example.com',
            'body': 'Отличная статья!',
        }, follow=True)

        self.assertEqual(response.status_code, 200)

        comments = self.published_post.comments.all()
        self.assertEqual(comments.count(), 1)

        comment = comments.first()
        self.assertEqual(comment.name, 'Вова')
        self.assertEqual(comment.body, 'Отличная статья!')

        self.assertContains(response, 'Отличная статья!')







