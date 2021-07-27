from django.shortcuts import render, get_object_or_404, redirect

from .models import Board, Topic, Post
from django.contrib.auth.models import User
from .forms import NewTopicForm, PostForm
from django.contrib.auth.decorators import login_required
from django.db.models import Count

from django.views.generic import UpdateView, ListView
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.urls import reverse

def home(request):
    boards=Board.objects.all()#Boardテーブルのオブジェクトのリストを「boards」に代入
    return render(request, 'home.html', {'boards':boards})#ブラウザの「request」に対して、変数「boards」を’home.html’の’boards’として渡して表示する。

class BoardListView(ListView):
    model=Board
    context_object_name='boards'
    template_name='home.html'

# def board_topics(request, pk):
#     board = get_object_or_404(Board,pk=pk)#pkで指定したBoardオブジェクトを「board」に代入してオブジェクトを生成するが、これが存在しない場合は404エラーメッセージを生成する
#     topics = board.topics.order_by('-last_updated').annotate(replies=Count('posts')-1)
#     return render(request, 'topics.html',{'board':board, 'topics':topics})#ブラウザの「request」に対して、変数「board」を’topics.html’の’board’として渡し表示する

class TopicListView(ListView):
    model=Topic
    context_object_name='topics'
    template_name='topics.html'
    paginate_by=2

    def get_context_data(self, **kwargs):
        # kwargs['board']=self.board
        # return super().get_context_data(**kwargs)
        context=super().get_context_data(**kwargs)
        context['board']=self.board
        # print(context)
        return context

    def get_queryset(self):
        self.board=get_object_or_404(Board, pk=self.kwargs.get('pk'))
        queryset=self.board.topics.order_by('-last_updated').annotate(replies=Count('posts')-1)
        # print(self.board)
        return queryset


@login_required
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)#boardオブジェクトを作成、該当なければ404エラーを表示
    #user = User.objects.first() #TODO:get the currently logged in user ユーザオブジェクトを生成し、最近ログインしたユーザを抽出

    if request.method == 'POST':#POST通信がrequestとして受け取られた場合の処理
        form = NewTopicForm(request.POST)#post通信でのレスポンスになる
        if form.is_valid():
            topic = form.save(commit=False)#NewTopicFormに入力されたデータをDB登録する前の状態で呼び出す
            topic.board = board#NewTopicFormのベースとなるTopicモデルのboardフィールドに登録
            topic.starter = request.user#NewTopicFormのベースとなるTopicモデルのstarterフィールドに登録
            topic.save()#TopicモデルのDB登録を実行
            post = Post.objects.create(#Postオブジェクトを生成し、下記のデータを登録
                message=form.cleaned_data.get('message'),#メッセージ(記事）form.is_validで検証後のmessageデータを登録
                topic=topic,#Topic(上記で生成したオブジェクト）
                created_by=request.user#ユーザ（編集者）
            )
            return redirect('topic_posts', pk=board.pk, topic_pk=topic.pk)#TODO:redirect to the created topic page　boardのpkに該当するトピック一覧を表示する
    else:
        form = NewTopicForm()#NewTopicFormに何も登録データがない状態のフォームをformに代入⇒get通信になる
    return render(request, 'new_topic.html', {'board': board, 'form':form})#new_topic.htmlを表示（受け取ったrequestがPOST通信出なかったときの処理）

# def topic_posts(request, pk, topic_pk):#topic_posts.htmlを表示する。
#     topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk )
#     topic.views+=1
#     topic.save()
#     return render(request, 'topic_posts.html', {'topic':topic})

class PostListView(ListView):
    model=Post
    context_object_name='posts'
    template_name='topic_posts.html'
    paginate_by=2

    def get_context_data(self, **kwargs):

        session_key='viewed_topic_{}'.format(self.topic.pk)
        if not self.request.session.get(session_key, False):
            self.topic.views+=1
            self.topic.save()
            self.request.session[session_key]=True
        # kwargs['topic']=self.topic
        # return super().get_context_data(**kwargs)
        context=super().get_context_data(**kwargs)
        context['topic']=self.topic
        # print(context)
        return context

    def get_queryset(self):
        self.topic=get_object_or_404(Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        queryset=self.topic.posts.order_by('created_at')
        # print(self.topic.board.pk)
        return queryset

@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()

            topic.last_updated=timezone.now()
            topic.save()

            #return redirect('topic_posts', pk=pk, topic_pk=topic_pk)
            topic_url=reverse('topic_posts', kwargs={'pk':pk, 'topic_pk':topic_pk})
            topic_post_url='{url}?page={page}#{id}'.format(
                url=topic_url,
                id=post.pk,
                page=topic.get_page_count()
            )
            return redirect(topic_post_url)
    else:
        form = PostForm()

    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})

@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message',)
    template_name = 'edit_post.html'
    pk_url_kwarg ='post_pk'
    context_object_name = 'post'

    def get_queryset(self):
        queryset=super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self,form):
        post = form.save(commit=False)
        post.update_by = self.request.user
        post.update_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)
