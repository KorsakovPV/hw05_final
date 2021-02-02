"""Формы для приложения users."""
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class CreationForm(UserCreationForm):
    """Класс дляформы регистрации user."""

    class Meta(UserCreationForm.Meta):
        """Указываем модель и какие поля из нее использовать."""

        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
