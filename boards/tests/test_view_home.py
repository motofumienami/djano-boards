from django.test import TestCase
from django.urls import reverse, resolve

from ..models import Board
from ..views import BoardListView


class Hometests(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name='Django', description= 'Django board.')
        url=reverse('home')#view名'home'で返されるURLを変数「url」に代入
        self.response=self.client.get(url)#変数「url」のurlにクライアントがアクセスしたときのレスポンスオブジェクトを変数「response」に代入

    def test_home_view_status_code(self):#「'home'」viewが正常なレスポンスを返すか検証
        self.assertEquals(self.response.status_code, 200)#変数responseのステータスコードが200であるか検証

    def test_home_url_resolves_home_view(self):#「’/’」リクエストが「home」view関数で解決するか検証
        view=resolve('/')#「'/'」でリクエストしたときに解決されるオブジェクトを変数「view」に代入
        #self.assertEquals(view.func, home)#変数「view」のfuncが「home」であるか否かを検証
        self.assertEquals(view.func.view_class, BoardListView)

    def test_home_view_contains_link_to_topics_page(self):
        board_topics_url = reverse('board_topics', kwargs={'pk': self.board.pk})#boardインスタンスのpk値を付けた「board_topics」ビューで返されるURLを「boardtopics_url」に代入
        self.assertContains(self.response, 'href="{0}"'.format(board_topics_url))#homeのレスポンスに「board_topics_url」へのリンクがあるか否かを検証
