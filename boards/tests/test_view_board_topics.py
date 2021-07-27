from django.test import TestCase
from django.urls import reverse, resolve

from ..models import Board
from ..views import TopicListView


class BoardTopicsTests(TestCase):
    def setUp(self):#セットアップメソッド：テストで使用するBoardインスタンスを作成
        Board.objects.create(name='Django', description='Django board.')

    def test_board_topics_view_success_status_code(self):#pK=1のBoardが存在するか否か
        url = reverse('board_topics', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_board_topics_view_not_found_status_code(self):#pk=99のBoardが存在しないか否か
        url = reverse('board_topics', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_board_topics_url_resolves_board_topics_view(self):#正しいビュー関数が使用されるのか
        view = resolve('/boards/1/')
        self.assertEquals(view.func.view_class, TopicListView)

    def test_board_topics_view_contains_navigation_links(self):#board_Topicsページにナビゲーションリンクがあるのか
        board_topics_url = reverse('board_topics', kwargs={'pk': 1})#キーワードとしてpk=1のboard_topicsへのURLを作成
        response = self.client.get(board_topics_url)#pk=1のboard_topicsページのインスタンス
        homepage_url = reverse('home')#homeページへのURL
        new_topic_url = reverse('new_topic',kwargs={'pk': 1})#キーワードとしてpk=1のnew_topicへのURLを作成
        self.assertContains(response, 'href="{0}"'.format(homepage_url))#pk=1のboard_topicseページにhomeへのリンクが含まれているか否か
        self.assertContains(response, 'href="{0}"'.format(new_topic_url))#pk=1のboard_topicsページにnew_topicへのリンクが含まれているか否か
