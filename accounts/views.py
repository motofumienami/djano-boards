from django.shortcuts import render, redirect
from .forms import SignUpForm
from django.contrib.auth import login as auth_login

from django.views.generic import UpdateView
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy

# Create your views here.
def signup(request):#リクエスト"signup/”で呼ばれるview関数
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid(): #データが検証できた時の処理
            user=form.save()
            auth_login(request, user)
            return redirect('home')
        #else:#データが検証できなかったときの処理＝特に何もしないで、POST受信したデータを持った’form’で’signup.html’をレンダリング。
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    models=User
    fields=('first_name', 'last_name', 'email')
    template_name='my_account.html'
    success_url=reverse_lazy('my_account')

    def get_object(self):
        # print(self.request.user.first_name)
        return self.request.user
