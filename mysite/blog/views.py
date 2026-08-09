from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.views.generic import ListView, FormView, CreateView
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector
from django.conf import settings


class PostCommentView(CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/post/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.blog_post = get_object_or_404(Post, id=kwargs['post_id'], status=Post.Status.PUBLISHED)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.post = self.blog_post
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.blog_post
        return context

    def get_success_url(self):
        return self.blog_post.get_absolute_url()

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



def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                                   status=Post.Status.PUBLISHED,
                                   publish__year=year,
                                   publish__month=month,
                                   publish__day=day)

    comments = post.comments.filter(active=True)
    form = CommentForm()

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    return render(request,
                  'blog/post/detail.html',
                  {'post': post, 'comments': comments, 'form': form, 'similar_posts': similar_posts})



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
        if 'query' in request.GET:
            if form.is_valid():
                query = form.cleaned_data['query']
                results = Post.published.annotate(search=SearchVector('title', 'body')).filter(search=query)
        return self.render_to_response(self.get_context_data(form=form, query=query, results=results))

