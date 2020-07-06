import time

from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Follow, Group, Post, User

DUMMY_CACHE = {
    'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}
}


class TestProfile(TestCase):
    def setUp(self):
        self.client = Client()

    def test_profile_new_user(self):
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
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='skywocker3',
                                             email='l.skywocker@dethstar.com',
                                             password='skywockerisjedi')

    def test_new_post_authorized_user(self):
        self.client.force_login(self.user)
        self.client.post(reverse('new_post'),
                         {'text': 'test_new_post_authorized'}, follow=True)
        self.assertEqual(Post.objects.all().count(), 1)
        last_post = Post.objects.last()
        self.assertEqual(last_post.text, 'test_new_post_authorized')

        self.assertEqual(last_post.author, self.user)

    def test_new_post_not_authorized_user(self):
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
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='skywocker3',
                                             email='l.skywocker@dethstar.com',
                                             password='skywockerisjedi')
        self.client.force_login(self.user)
        self.post = Post.objects.create(text='TEST_POST_1', author=self.user)

    def test_edit_post_authorized(self):
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
    def setUp(self):
        self.client = Client()

    def test_page_not_found(self):
        url_post_view = reverse('post_view', kwargs={'username': 'pavel',
                                                     'post_id': 2})
        response = self.client.get(url_post_view)
        self.assertTemplateUsed(response, 'misc/404.html')
        self.assertEqual(response.status_code, 404)


class TestPostImages(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='skywocker3',
                                             email='l.skywocker@dethstar.com',
                                             password='skywockerisjedi')
        self.client.force_login(self.user)
        self.group = Group.objects.create(title='harvester',
                                          description='harvester',
                                          slug='harvester')
        self.path_img = '/home/pavel/Dev/hw05_final/media/posts/Korra.jpg'
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
        last_post = Post.objects.last()
        url_post_view = reverse('post_view',
                                kwargs={'username': last_post.author,
                                        'post_id': last_post.id})
        response = self.client.get(url_post_view)
        self.assertContains(response, '<img')

    def test_profile_images(self):
        last_post = Post.objects.last()
        url_profile = reverse('profile', kwargs={'username': last_post.author})
        response = self.client.get(url_profile)
        self.assertContains(response, '<img')

    @override_settings(CACHES=DUMMY_CACHE)
    def test_index_images(self):
        url_index = reverse('index')
        response = self.client.get(url_index)
        self.assertContains(response, '<img')

    def test_group_view_images(self):
        url_group_view = reverse('group_view',
                                 kwargs={'slug': self.group.slug})
        response = self.client.get(url_group_view)
        self.assertContains(response, '<img')

    def test_load_images(self):
        self.path_img = '/home/pavel/Dev/hw05_final/media/posts/picture.txt'
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
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='skywocker3',
                                             email='l.skywocker@dethstar.com',
                                             password='skywockerisjedi')
        self.client.force_login(self.user)
        self.post = Post.objects.create(text='TEST_POST_1', author=self.user)

    def test_index_cache(self):
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
    def setUp(self):
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
        url_profile = reverse('profile',
                              kwargs={'username': self.user2.username})
        response_profile = self.client.get(url_profile)
        self.assertContains(response_profile, 'Подписаться')

    def test_double_follow(self):
        url_profile_follow = reverse('profile_follow',
                                     kwargs={'username': self.user2.username})
        self.client.get(url_profile_follow, follow=True)
        self.assertEqual(Follow.objects.all().count(), 1)
        self.client.get(url_profile_follow, follow=True)
        self.assertEqual(Follow.objects.all().count(), 1)

    def test_self_follow(self):
        url_profile_follow = reverse('profile_follow',
                                     kwargs={'username': self.user1.username})
        self.assertEqual(Follow.objects.all().count(), 0)
        self.client.get(url_profile_follow, follow=True)
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_unfollow(self):
        Follow.objects.create(user_id=self.user1.id, author_id=self.user2.id)
        self.assertEqual(Follow.objects.all().count(), 1)
        url_profile = reverse('profile',
                              kwargs={'username': self.user2.username})
        response_profile = self.client.get(url_profile, follow=True)
        self.assertContains(response_profile, 'Отписаться')

    def test_follow_index(self):
        url_follow_index = reverse('follow_index')
        response_profile = self.client.get(url_follow_index)
        self.assertNotContains(response_profile, 'TEST_POST_1')

        Follow.objects.create(user_id=self.user1.id, author_id=self.user2.id)

        response_profile = self.client.get(url_follow_index)
        self.assertContains(response_profile, 'TEST_POST_1')


class TestComment(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='skywocker1',
                                              email='l.skywocker@dethstar.com',
                                              password='skywockerisjedi')
        self.user2 = User.objects.create_user(username='skywocker2',
                                              email='l.skywocker@dethstar.com',
                                              password='skywockerisjedi')
        self.post = Post.objects.create(text='TEST_POST_1', author=self.user1)

    def test_comment_not_authorized_user(self):
        url_comment = reverse('add_comment',
                              kwargs={'username': self.post.author.username,
                                      'post_id': self.post.id})
        url = '/auth/login/?next={}'.format(url_comment)
        response_comment = self.client.get(url_comment)
        self.assertRedirects(response_comment, url, status_code=302,
                             target_status_code=200, msg_prefix='',
                             fetch_redirect_response=True)

    def test_comment_authorized_user(self):
        self.client.force_login(self.user1)
        url_comment = reverse('add_comment',
                              kwargs={'username': self.post.author.username,
                                      'post_id': self.post.id})
        response_comment = self.client.post(url_comment, {'text': 'Comment 1'},
                                            follow=True)
        self.assertContains(response_comment, 'Comment 1')
