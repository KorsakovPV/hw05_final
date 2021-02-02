"""Формы приложения posts."""
from django import forms

from posts.models import Comment, Post


class PostForm(forms.ModelForm):
    """Форма создания и редактирования поста."""

    class Meta:
        """Указываем связанную модель и нужные нам поля."""

        model = Post
        fields = ('group', 'text', 'image')


class CommentForm(forms.ModelForm):
    """Форма создания и редактирования комментария."""

    class Meta:
        """Указываем связанную модель и нужные нам поля."""

        model = Comment
        fields = ('text',)
