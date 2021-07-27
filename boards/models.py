from django.db import models#すべてのモデルは"django.db.models"クラスのmodels.Model"というサブクラスなので、modelsクラスをインポート
# Create your models here.
from django.contrib.auth.models import User#ビルトインされたUserモデルの利用設定
from django.utils.text import Truncator#djangoにビルトインされているTruncatorメソッドをインポート
from django.utils.html import mark_safe
from markdown import markdown
import math
#Boardモデルを作成
class Board(models.Model):
    name = models.CharField(max_length=30, unique=True)#name最大文字30、ユニーク設定
    description = models.CharField(max_length=100)#Boardの説明、概要　最大100文字

    def __str__(self):#インスタンスが呼ばれたとき、nameを返すようにする
        return self.name#当該インスタンスのnameを返す

    def get_posts_count(self):#当該インスタンスに属しているPostの数を返す
        return Post.objects.filter(topic__board=self).count()

    def get_last_post(self):#当該インスタンスに属している最終のPostオブジェクトを返す
        return Post.objects.filter(topic__board=self).order_by('-created_at').first

#Topicモデルを作成
class Topic(models.Model):
    subject = models.CharField(max_length=255)#題名 最大255文字
    last_updated = models.DateTimeField(auto_now_add=True)#最終更新日　自動で記録
    board = models.ForeignKey(Board, on_delete=models.PROTECT, related_name='topics')#属するBoard Boardモデルとの関連キー　関連の名前：topics
    starter = models.ForeignKey(User, on_delete=models.PROTECT, related_name='topics')#作成者　Userモデルとの関連キー　関連の名前：topics
    views = models.PositiveIntegerField(default=0)

    def __str__(self):#インスタンスが呼ばれたとき、subjectを返すようにする
        return self.subject#当該インスタンスのsubjectを返す

    def get_page_count(self):#topicごとのページ数を返すメソッド
        count=self.posts.count()
        pages=count/2
        return math.ceil(pages) #小数点以下を切上げ（ceil)

    def has_many_pages(self, count=None):#topicごとのページ数が６を超えるtrue,超えないfalse
        if count is None:
            count=self.get_page_count()
        return count > 6#

    def get_page_range(self):#topicごとのページ数に応じた枠の範囲を返す。最低５.
        count=self.get_page_count()
        if self.has_many_pages(count):
            return range(1,5)
        return range(1, count +1)

    def get_last_five_posts(self):
        return self.posts.order_by('-created_at')[:5]#「created_at」で降順で並べ替えて、上から5件分を取得して返す。




#Postモデルを作成
class Post(models.Model):
    message = models.TextField(max_length=4000)#メッセージ　最大4000文字
    topic = models.ForeignKey(Topic, on_delete=models.PROTECT, related_name='posts')#属するTopic Topicモデルとの関連キー　関連の名前：posts
    created_at = models.DateTimeField(auto_now_add=True)#投稿作成日　自動で記録
    updated_at = models.DateTimeField(null=True)#更新日　nullでもよい
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='posts')#作成者　Userモデルとの関連キー　関連の名前：posts
    updated_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True ,related_name='+')#更新者　Userモデルとの関連キー　関連の名前：＋

    def __str__(self):#インスタンスが呼ばれたときに、turncated_messageを返すようにする
        truncated_message = Truncator(self.message)
        return truncated_message.chars(30)

    def get_message_as_markdown(self):
        return mark_safe(markdown(self.message, safe_mode='escape'))
