![foodgram-project](https://github.com/KorsakovPV/hw05_final/workflows/test/badge.svg)

# hw05_final

Проект социальная сеть. Она даст пользователям возможность создать учетную запись, публиковать записи, подписываться на любимых авторов и отмечать понравившиеся записи.

## Установка:
1. Клонируйте репозиторий на локальную машину.
- ``git clone https://github.com/KorsakovPV/hw05_final``
2. Установите виртуальное окружение.
- ``python3 -m venv venv``
3. Активируйте виртуальное окружение.
- ``source venv/bin/activate``
4. Установите зависимости.
- ``pip install -r requirements.txt``
5. Выполните миграции.
- ``python manage.py migrate``
6. Запустите локальный сервер.
- ``python manage.py runserver``
