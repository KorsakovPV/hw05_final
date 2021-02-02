"""Описание страницы администратора для приложения posts."""
from django.contrib import admin

from .models import Comment, Follow, Group, Post


class PostAdmin(admin.ModelAdmin):
    """Описание полей модели Post для сайта администрирования."""

    list_display = ('pk', 'text', 'author', 'group', 'pub_date', 'image')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    """Описание полей модели Group для сайта администрирования."""

    list_display = ('pk', 'title', 'description', 'slug')
    search_fields = ('title',)
    list_filter = ('slug',)
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    """Описание полей модели Comment для сайта администрирования."""

    list_display = ('pk', 'author', 'text', 'created', 'post')
    search_fields = ('author', 'post')
    list_filter = ('author', 'post')
    empty_value_display = '-пусто-'


class FollowAdmin(admin.ModelAdmin):
    """Описание полей модели Follow для сайта администрирования."""

    list_display = ('pk', 'author', 'user')
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')
    empty_value_display = '-пусто-'


admin.site.register(Group, GroupAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
