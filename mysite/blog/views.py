from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.views.generic import ListView, FormView, CreateView, DetailView
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from django.contrib.postgres.search import TrigramSimilarity
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST

from .models import Post, Comment
from taggit.models import Tag


@method_decorator(require_POST, name='dispatch')
class PostCommentView(CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/post/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.blog_post = get_object_or_404(Post, id=kwargs['post_id'], status=Post.Status.PUBLISHED)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.post = self.blog_post
        comment.save()
        return self.render_to_response(
            self.get_context_data(form=form, comment=comment)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.blog_post
        if 'comment' in kwargs:
            context['comment'] = kwargs['comment']
        return context

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        tag_slug = self.kwargs.get('tag_slug')
        if tag_slug:
            self.tag = get_object_or_404(Tag, slug=tag_slug)
            queryset = queryset.filter(tags__in=[self.tag])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, 'tag'):
            context['tag'] = self.tag
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post/detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        return get_object_or_404(
            Post,
            status=Post.Status.PUBLISHED,
            slug=self.kwargs['post'],
            publish__year=self.kwargs['year'],
            publish__month=self.kwargs['month'],
            publish__day=self.kwargs['day']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(active=True)
        context['form'] = CommentForm()

        post_tags_ids = self.object.tags.values_list('id', flat=True)
        similar_posts = Post.published.filter(
            tags__in=post_tags_ids
        ).exclude(id=self.object.id)

        context['similar_posts'] = similar_posts.annotate(
            same_tags=Count('tags')
        ).order_by('-same_tags', '-publish')[:4]




class PostShareView(FormView):
    form_class = EmailPostForm
    template_name = 'blog/post/share.html'

    def dispatch(self, request, *args, **kwargs):
        self.blog_post = get_object_or_404(Post, id=kwargs['post_id'], status=Post.Status.PUBLISHED)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.blog_post
        return context

    def form_valid(self, form):
        cd = form.cleaned_data
        post_url = self.request.build_absolute_uri(self.blog_post.get_absolute_url())
        subject = f"{cd['name']} recommends you read {self.blog_post.title}."
        message = (
            f"Read {self.blog_post.title} at {post_url}\n"
            f"{cd['name']}'s comments: {cd['comments']}"
        )
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [cd['to']],
        )
        context = self.get_context_data(sent=True)
        return self.render_to_response(context)



class PostSearchView(FormView):
    form_class = SearchForm
    template_name = 'blog/post/search.html'

    def get(self, request, *args, **kwargs):
        query = None
        results = []
        form = self.form_class(request.GET)
        if 'query' in request.GET and form.is_valid():
            query = form.cleaned_data['query']
            results = Post.published.annotate(similarity=TrigramSimilarity('title', query)).filter(similarity__gt=0.1).order_by('-similarity')
        return self.render_to_response(self.get_context_data(form=form, query=query, results=results))

