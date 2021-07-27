from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from ..views import signup
from ..forms import SignUpForm #UserCreationForm

# Create your tests here.
class SignUpTests(TestCase):
    def setUp(self):#「'signup'」でURLリクエストしたときのレスポンスをテストする。(setup)
        url = reverse('signup')
        self.response = self.client.get(url)

    def test_signup_status_code(self):#１．サインアップページにアクセスが成功するか否か。(test_signup_status_code)
        self.assertEquals(self.response.status_code, 200)

    def test_signup_url_resolves_signup_view(self):#２．「'/signup/'」へのpathで解決するURLでのリクエストで「signup」view関数を呼ぶか否か
        view = resolve('/signup/')
        self.assertEquals(view.func, signup)

    def test_csrf(self):#３．「'signup'」でURLリクエストしたときのレスポンスが、csrfトークンを含んでいるか否か
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):#４．「'signup'」でURLリクエストしたときのレスポンスに含まれるフォームが、「SignUpForm」であるか否か。(test_contains_form)
        form = self.response.context.get('form')
        self.assertIsInstance(form, SignUpForm)

    def test_form_inputs(self):#５．「'signup'」でURLリクエストしたときのレスポンスに、５つ（csrf, username, email, password1, password2）の「<inputs」があり、Type=Textが1つ、Type=emailが一つ、Type=passwordが２つが含まれているか否k
        '''
        The view must contain five inputs: csrf, username, email,
        password1, password2
        '''
        self.assertContains(self.response, '<input', 5)
        self.assertContains(self.response, 'type="text"', 1)
        self.assertContains(self.response, 'type="email"', 1)
        self.assertContains(self.response, 'type="password"', 2)

class SuccessfulSignUpTests(TestCase):#⇒テストの視点：siguupしたらどうなるのか？
    def setUp(self):#'username'='john'　'email'='john@doe.com'  'passaword1'='abcdef123456' 'password2'='abcdef123456'というテストデータをもって登録（signup）のテストを行う。(setup)
        url = reverse('signup')
        data = {
            'username': 'john',
            'email': 'john@doe.com',
            'password1': 'abcdef123456',
            'password2': 'abcdef123456'
        }
        self.response = self.client.post(url, data)
        self.home_url = reverse('home')

    def test_redirection(self):#１．検証フォームのサブミッションとして(検証後のアクション)「home.html」にリダイレクトする(test_redirection)
        '''
        A valid form submission should redirect the user to the home page
        '''
        self.assertRedirects(self.response, self.home_url)

    def test_user_creation(self):#２．Userオブジェクトが存在する。(test_user_creation)
        self.assertTrue(User.objects.exists())

    def test_user_authentication(self):#３．「’home’」でURLリクエストしたときのレスポンスに含まれる「User」は認証済みである。(test_user_authentication)
        '''
        Create a new request to an arbitrary page.
        The resulting response should now have a `user` to its context,
        after a successful sign up.
        '''
        response = self.client.get(self.home_url)
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated)

class InvalidSignUpTests(TestCase):#データが検証できなかった場合のシナリオを基にしたテスト：「InvalidSignUpTests」

    def setUp(self):#空欄でsignupをリクエストしたときに受けるレスポンスのテストを行う。(setup)
        url = reverse('signup')
        self.response = self.client.post(url, {})  # submit an empty dictionary

    def test_signup_status_code(self):#１．空欄でsignupページから送信（POST送信）しても、アクセス自体は成功する(test_signup_status_code)
        '''
        An invalid form submission should return to the same page
        '''
        self.assertEquals(self.response.status_code, 200)

    def test_form_errors(self):#２．そのレスポンスに含まれる「form」はエラーフォームである。(test_form_errors)
        form = self.response.context.get('form')
        self.assertTrue(form.errors)

    def test_dont_create_user(self):#３．Userオブジェクトは存在しない。(test_dont_create_user)
        self.assertFalse(User.objects.exists())

# class logOutTests(TestCase):
#     def setUp(self):#「'logout'」でリクエストされたときのレスポンスをテストする
#
#
#     def test_logout_status_code(self):#ログアウトしたときのアクセスが成功するかいなか
#         self.assertEquals(self.response.status_code, 200)
