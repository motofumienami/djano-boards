from django.test import TestCase
from django.urls import resolve, reverse
from django.contrib.auth.models import User
from django.forms import ModelForm
from ..views import UserUpdateView

class UserUpdateViewTestCase(TestCase):
    def setUp(self):
        self.username = 'john'
        self.password = 'secret123'
        self.user = User.objects.create_user(username=self.username, email='john@doe.com', password=self.password)
        self.url = reverse('my_account')

class LoginRequiredUserUpdateViewTests(UserUpdateViewTestCase):
    def test_redirection(self):
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))


class UserUpdateViewTests(UserUpdateViewTestCase):
    def setUp(self):
        super().setUp()
        # self.username = 'john'
        # self.password = 'secret123'
        # self.user = User.objects.create_user(username=self.username, email='john@doe.com', password=self.password)
        self.client.login(username=self.username, password=self.password)#上記の条件でログインしたクライアントを作成
        self.response = self.client.get(self.url)#作成したクライアントで当該urlへアクセスしたときの反応をオブジェクト化

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_url_resolves_correct_view(self):
        view = resolve('/settings/account/')
        self.assertEquals(view.func.view_class, UserUpdateView)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, ModelForm)

    def test_form_inputs(self):
        '''
        The view must contain two inputs: csrf, first_name, last_name, email_address
        '''
        self.assertContains(self.response, '<input', 4)

class SuccessfulUserUpdateViewTests(UserUpdateViewTestCase):
    def setUp(self):
        super().setUp()
        # self.username = 'john'
        # self.password = 'secret123'
        # self.user = User.objects.create_user(username=self.username, email='john@doe.com', password=self.password)

        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {'first_name': 'jo', 'last_name':'hn'})

    def test_redirection(self):
        '''
        A valid form submission should redirect the user
        '''
        my_account_url = reverse('my_account')
        self.assertRedirects(self.response, my_account_url)

    def test_user_changed(self):
        self.user.refresh_from_db()
        self.assertEquals({self.user.first_name,self.user.last_name}, {'jo','hn'})
