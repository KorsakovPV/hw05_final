"""Файл конфигурации для приложения posts."""
from django.apps import AppConfig


class PostsConfig(AppConfig):
    """
    Подключение приложения posts.

    Для настройки приложения создаем класс наследник AppConfig и указываем
    путь для его импорта в INSTALLED_APPS.

    """

    name = 'posts'
