"""Файл views для приложения posts."""
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from posts.forms import CommentForm, PostForm
from posts.models import Follow, Group, Post, User


def index(request):
    """Страница индекс."""
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html',
                  {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    """Страница для группы."""
    group = get_object_or_404(Group, slug=slug)
    posts = group.group_posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group,
                                          'page': page,
                                          'paginator': paginator})


@login_required
def new_post(request):
    """Создание нового поста."""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    """Страница для профиля."""
    author = get_object_or_404(User, username=username)
    post_list = author.author_posts.all()
    if request.user.is_anonymous:
        is_follow = False
    else:
        is_follow = Follow.objects.filter(author=author,
                                          user=request.user).exists()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html',
                  {'author': author,
                   'page': page,
                   'paginator': paginator,
                   'is_follow': is_follow,
                   })


def post_view(request, username, post_id):
    """Страница одного поста."""
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(author.author_posts, id=post_id)
    post_comments = post.post_comment.all()
    form = CommentForm()
    return render(request, 'post.html',
                  {'author': author, 'post': post,
                   'form': form,
                   'post_comments': post_comments})


@login_required
def post_edit(request, username, post_id):
    """Страница редактирования поста."""
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(author.author_posts, id=post_id)
    if request.user == author:
        form = PostForm(request.POST or None, files=request.FILES or None,
                        instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_view',
                            username=username,
                            post_id=post_id)
        return render(request, 'new_post.html',
                      {'form': form,
                       'post': post})
    else:
        return redirect('post_view', username=username, post_id=post_id)


def page_not_found(request, exception):
    """Страница 404."""
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    """Страница 500."""
    return render(request, 'misc/500.html', status=500)


@login_required
def add_comment(request, username, post_id):
    """Добавление комментария."""
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(author.author_posts, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post_id = post_id
        comment.save()
        return redirect('post_view',
                        username=username,
                        post_id=post_id)
    return render(request, 'comments.html',
                  {'form': form, 'post': post})


@login_required
def follow_index(request):
    """Страница постов подписанных авторов."""
    user = get_object_or_404(User, username=request.user)
    follower = user.follower.all().values('author')
    post_follower = Post.objects.filter(author__in=follower).order_by(
        '-pub_date')
    paginator = Paginator(post_follower, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html',
                  {'page': page, 'paginator': paginator})


@login_required
def profile_follow(request, username):
    """Подписка на автора."""
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user_id=request.user.id,
                                     author_id=author.id)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Отписка от автора."""
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user_id=request.user.id,
                                   author_id=author.id)
    follow.delete()
    return redirect('profile', username=username)
