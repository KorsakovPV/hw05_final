"""Тесты view функций приложения posts."""
import time

from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Follow, Group, Post, User
from yatube.settings import BASE_DIR

DUMMY_CACHE = {
    'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}
}


class TestProfile(TestCase):
    """Класс для тестирования страницы профиля."""

    def setUp(self):
        """Подготовка тестового окружения."""
        self.client = Client()

    def test_profile_new_user(self):
        """
        Тест страницы профиля.

        Для существующего пользователя ответ 200.
        Для не существующего пользователя ответ 404.

        """
        url_profile = reverse('profile',
                              kwargs={'username': 'skywocker3'})
        self.assertEqual(self.client.post(url_profile).status_code, 404)
        self.client.post(reverse('signup'),
                         {'first_name': 'Luke',
                          'last_name': 'Skywocker',
                          'username': 'skywocker3',
                          'email': 'l.skywocker@dethstar.com',
                          'password1': 'isjediskywockerisjedi',
                          'password2': 'isjediskywockerisjedi'}, follow=True)
        self.assertEqual(self.client.post(url_profile).status_code, 200)


class TestNewPost(TestCase):
    """Класс для тестирования страницы нового поста."""

    def setUp(self):
        """Подготовка тестового окружения."""
        self.client = Client()
        self.user = User.objects.create_user(username='skywocker3',
                                             email='l.skywocker@dethstar.com',
                                             password='skywockerisjedi')

    def test_new_post_authorized_user(self):
        """
        Тест страницы нового поста для авторизированного пользователя.

        Создается пост, проверяется что он появился в базе, проверяется текст
        на странице верный.

        """
        self.client.force_login(self.user)
        self.client.post(reverse('new_post'),
                         {'text': 'test_new_post_authorized'}, follow=True)
        self.assertEqual(Post.objects.all().count(), 1)
        last_post = Post.objects.last()
        self.assertEqual(last_post.text, 'test_new_post_authorized')

        self.assertEqual(last_post.author, self.user)

    def test_new_post_not_authorized_user(self):
        """
        Тест страницы нового поста для не авторизированного пользователя.

        Создается пост, проверяется что он не появился в базе.

        """
        response = self.client.get(reverse('new_post'))
        self.assertURLEqual(response.url,
                            '{}?next={}'.format(reverse('login'),
                                                reverse('new_post')),
                            msg_prefix='Неавторизованный посетитель не может '
                                       'опубликовать пост (его редиректит на '
                                       'страницу входа')
        self.assertEqual(Post.objects.all().count(), 0)

    @override_settings(CACHES=DUMMY_CACHE)
    def test_new_post_view(self):
        """
        Тест страницы просмотра поста для авторизированного пользователя.

        Создается пост, проверяется что он есть на странице поста, на профиле
        пользователя и на главной странице.
        Так как главная страница кеширована применяется декоратор.

        """
        self.client.force_login(self.user)
        self.post = Post.objects.create(text='TEST_POST_1', author=self.user)
        url_post_view = reverse('post_view',
                                kwargs={'username': self.user.username,
                                        'post_id': self.post.id})
        response_post_view = self.client.get(url_post_view)
        self.assertContains(response_post_view, self.post.text)
        url_profile = reverse('profile',
                              kwargs={'username': self.user.username})
        response_profile = self.client.get(url_profile)
        self.assertContains(response_profile, self.post.text)
        url_index = reverse('index')
        response_index = self.client.get(url_index)
        self.assertContains(response_index, self.post.text)


class TestPostEdit(TestCase):
    """Класс для проверки редактирования поста."""

    def setUp(self):
        """Подготовка тестового окружения."""
        self.client = Client()
        self.user = User.objects.create_user(username='skywocker3',
                                             email='l.skywocker@dethstar.com',
                                             password='skywockerisjedi')
        self.client.force_login(self.user)
        self.post = Post.objects.create(text='TEST_POST_1', author=self.user)

    def test_edit_post_authorized(self):
        """
        Тест страницы редактирования поста для авторизированного пользователя.

        Создается пост, проверяется что он есть на странице поста, на профиле
        пользователя и на главной странице.
        Так как главная страница кеширована применяется декоратор.

        """
        url_post_edit = reverse('post_edit',
                                kwargs={'username': self.user.username,
                                        'post_id': self.post.id})
        response = self.client.post(url_post_edit,
                                    {'text': 'TEST_POST_2'}, follow=True)
        self.post.text = 'TEST_POST_2'
        self.assertEqual(response.status_code, 200)
        url_post_view = reverse('post_view',
                                kwargs={'username': self.user.username,
                                        'post_id': self.post.id})
        response = self.client.get(url_post_view)
        self.assertContains(response, self.post.text)
        url_profile = reverse('profile',
                              kwargs={'username': self.user.username})
        response = self.client.get(url_profile)
        self.assertContains(response, self.post.text)
        response = self.client.get(reverse('index'))
        self.assertContains(response, self.post.text)


class TestPostErrors(TestCase):
    """Класс проверки вывода ошибок."""

    def setUp(self):
        """Подготовка тестового окружения."""
        self.client = Client()

    def test_page_not_found(self):
        """
        Тест 404.

        Делается запрос на заведомо не существующий пост и профиль. Проверяется
        что код ошибки 404. Проверяется что применен верный шаблон.

        """
        url_post_view = reverse('post_view', kwargs={'username': 'pavel',
                                                     'post_id': 2})
        response = self.client.get(url_post_view)
        self.assertTemplateUsed(response, 'misc/404.html')
        self.assertEqual(response.status_code, 404)

        url_post_view = reverse('profile', kwargs={'username': 'pavel'})
        response = self.client.get(url_post_view)
        self.assertTemplateUsed(response, 'misc/404.html')
        self.assertEqual(response.status_code, 404)


class TestPostImages(TestCase):
    """Класс тестирования изображений."""

    def setUp(self):
        """Подготовка тестового окружения."""
        self.client = Client()
        self.user = User.objects.create_user(username='skywocker3',
                                             email='l.skywocker@dethstar.com',
                                             password='skywockerisjedi')
        self.client.force_login(self.user)
        self.group = Group.objects.create(title='harvester',
                                          description='harvester',
                                          slug='harvester')
        self.path_img = f'{BASE_DIR}/posts/tests/test_media/Korra.jpg'
        with open(self.path_img, 'rb') as img:
            test_post = Post.objects.create(text='TEST_POST_1',
                                            author=self.user,
                                            group=self.group)
            url_edit_post = reverse(
                'post_edit',
                kwargs={'username': test_post.author.username,
                        'post_id': test_post.id})
            self.client.post(url_edit_post, {'author': self.user,
                                             'text': 'post with mmmmyy image',
                                             'image': img,
                                             'group': self.group.id})

    def test_post_view_images(self):
        """Проверяет наличие кактинки на странице поста."""
        last_post = Post.objects.last()
        url_post_view = reverse('post_view',
                                kwargs={'username': last_post.author,
                                        'post_id': last_post.id})
        response = self.client.get(url_post_view)
        self.assertContains(response, '<img')

    def test_profile_images(self):
        """Проверяет наличие кактинки на странице профиля."""
        last_post = Post.objects.last()
        url_profile = reverse('profile', kwargs={'username': last_post.author})
        response = self.client.get(url_profile)
        self.assertContains(response, '<img')

    @override_settings(CACHES=DUMMY_CACHE)
    def test_index_images(self):
        """Проверяет наличие кактинки на главной странице."""
        url_index = reverse('index')
        response = self.client.get(url_index)
        self.assertContains(response, '<img')

    def test_group_view_images(self):
        """Проверяет наличие кактинки на странице группы."""
        url_group_view = reverse('group_view',
                                 kwargs={'slug': self.group.slug})
        response = self.client.get(url_group_view)
        self.assertContains(response, '<img')

    def test_load_images(self):
        """Проверяет не валидная картинка не грузится."""
        self.path_img = f'{BASE_DIR}/posts/tests/test_media/picture.txt'
        with open(self.path_img, 'rb') as img:
            test_post = Post.objects.create(text='TEST_POST_1',
                                            author=self.user, group=self.group)
            url_edit_post = reverse('post_edit',
                                    kwargs={
                                        'username': test_post.author.username,
                                        'post_id': test_post.id})
            self.client.post(url_edit_post, {'author': self.user,
                                             'text': 'post with mmmmyy image',
                                             'image': img,
                                             'group': self.group.id})
        url_post_view = reverse('post_view',
                                kwargs={'username': test_post.author,
                                        'post_id': test_post.id})
        response = self.client.get(url_post_view)
        self.assertNotContains(response, '<img')


class TestCache(TestCase):
    """Класс для проверки кеширования."""

    def setUp(self):
        """Подготовка тестового окружения."""
        self.client = Client()
        self.user = User.objects.create_user(username='skywocker3',
                                             email='l.skywocker@dethstar.com',
                                             password='skywockerisjedi')
        self.client.force_login(self.user)
        self.post = Post.objects.create(text='TEST_POST_1', author=self.user)

    def test_index_cache(self):
        """
        Тест кеширования.

        Проверяется, что на странице есть пост 1 и нет поста 2.
        Редактируем пост.
        Проверяем вывод главной страницы. Там не отредактированный пост.
        Ждем больше чем в кеше указано времени

        """
        url_index = reverse('index')
        response_url_index = self.client.get(url_index)
        self.assertNotContains(response_url_index, 'TEST_POST_2')
        self.assertContains(response_url_index, 'TEST_POST_1')

        url_post_edit = reverse('post_edit',
                                kwargs={'username': self.user.username,
                                        'post_id': self.post.id})
        response_url_post_edit = self.client.post(url_post_edit,
                                                  {'text': 'TEST_POST_2'},
                                                  follow=True)
        self.assertEqual(response_url_post_edit.status_code, 200)

        url_index = reverse('index')
        response_url_index = self.client.get(url_index)
        self.assertNotContains(response_url_index, 'TEST_POST_2')
        self.assertContains(response_url_index, 'TEST_POST_1')

        time.sleep(20)

        url_index = reverse('index')
        response_url_index = self.client.get(url_index)
        self.assertNotContains(response_url_index, 'TEST_POST_1')
        self.assertContains(response_url_index, 'TEST_POST_2')


class TestFollow(TestCase):
    """Класс тестирования подписок."""

    def setUp(self):
        """Подготовка тестового окружения."""
        self.client = Client()
        self.user1 = User.objects.create_user(username='skywocker1',
                                              email='l.skywocker@dethstar.com',
                                              password='skywockerisjedi')
        self.user2 = User.objects.create_user(username='skywocker2',
                                              email='l.skywocker@dethstar.com',
                                              password='skywockerisjedi')
        self.client.force_login(self.user1)
        self.post = Post.objects.create(text='TEST_POST_1', author=self.user2)

    def test_follow(self):
        """
        Тест подписки.

        Проверяется, что на странице профиля есть кнопка подписаться.

        """
        url_profile = reverse('profile',
                              kwargs={'username': self.user2.username})
        response_profile = self.client.get(url_profile)
        self.assertContains(response_profile, 'Подписаться')

    def test_double_follow(self):
        """
        Тест подписки и повторной подписки.

        Проверяется, что после подписки в базе появится запись, а повторная
        подписка не изменит состояние базы.

        """
        url_profile_follow = reverse('profile_follow',
                                     kwargs={'username': self.user2.username})
        self.client.get(url_profile_follow, follow=True)
        self.assertEqual(Follow.objects.all().count(), 1)
        self.client.get(url_profile_follow, follow=True)
        self.assertEqual(Follow.objects.all().count(), 1)

    def test_self_follow(self):
        """
        Тест подписки на самого себя.

        Проверяется, что подписка на самого себя не изменит состояние базы.
        Подписка не удастся.

        """
        url_profile_follow = reverse('profile_follow',
                                     kwargs={'username': self.user1.username})
        self.assertEqual(Follow.objects.all().count(), 0)
        self.client.get(url_profile_follow, follow=True)
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_unfollow(self):
        """
        Тест отписки.

        Проверяется, что на странице профиля у подписанного пользователя есть
        кнопка отписаться.

        """
        Follow.objects.create(user_id=self.user1.id, author_id=self.user2.id)
        self.assertEqual(Follow.objects.all().count(), 1)
        url_profile = reverse('profile',
                              kwargs={'username': self.user2.username})
        response_profile = self.client.get(url_profile, follow=True)
        self.assertContains(response_profile, 'Отписаться')

    def test_follow_index(self):
        """
        Тест страницы подписанных пользователей.

        Проверяется, что подписка на самого себя не изменит состояние базы.
        Подписка не удастся.

        """
        url_follow_index = reverse('follow_index')
        response_profile = self.client.get(url_follow_index)
        self.assertNotContains(response_profile, 'TEST_POST_1')

        Follow.objects.create(user_id=self.user1.id, author_id=self.user2.id)

        response_profile = self.client.get(url_follow_index)
        self.assertContains(response_profile, 'TEST_POST_1')


class TestComment(TestCase):
    """Класс тестирования комментариев."""

    def setUp(self):
        """Подготовка тестового окружения."""
        self.client = Client()
        self.user1 = User.objects.create_user(username='skywocker1',
                                              email='l.skywocker@dethstar.com',
                                              password='skywockerisjedi')
        self.user2 = User.objects.create_user(username='skywocker2',
                                              email='l.skywocker@dethstar.com',
                                              password='skywockerisjedi')
        self.post = Post.objects.create(text='TEST_POST_1', author=self.user1)

    def test_comment_not_authorized_user(self):
        """
        Тест комментариев для не ваторезированного пользователя.

        Проверяется, не авторизированный пользователь не может оставлять
        комментарии. Перенаправляется на страницу регистрации.

        """
        url_comment = reverse('add_comment',
                              kwargs={'username': self.post.author.username,
                                      'post_id': self.post.id})
        url = '/auth/login/?next={}'.format(url_comment)
        response_comment = self.client.get(url_comment)
        self.assertRedirects(response_comment, url, status_code=302,
                             target_status_code=200, msg_prefix='',
                             fetch_redirect_response=True)

    def test_comment_authorized_user(self):
        """
        Тест комментариев для ваторезированного пользователя.

        Проверяется, авторизированный пользователь может оставлять комментарии.

        """
        self.client.force_login(self.user1)
        url_comment = reverse('add_comment',
                              kwargs={'username': self.post.author.username,
                                      'post_id': self.post.id})
        response_comment = self.client.post(url_comment, {'text': 'Comment 1'},
                                            follow=True)
        self.assertContains(response_comment, 'Comment 1')
