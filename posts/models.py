from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField('Дата публикации',
                                    auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Автор',
                               related_name='author_posts')
    group = models.ForeignKey(Group,
                              on_delete=models.SET_NULL,
                              blank=True,
                              null=True,
                              verbose_name='Группа',
                              related_name='group_posts')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             verbose_name='Пост',
                             related_name='post_comment')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Автор',
                               related_name='author_comment')
    text = models.TextField(blank=False,
                            verbose_name='Текст коментария')
    created = models.DateTimeField(auto_now_add=True,
                                   editable=False)

    class Meta:
        ordering = ['-created']


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             blank=False,
                             null=False,
                             related_name='follower')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=False,
                               null=False,
                               related_name='following')
