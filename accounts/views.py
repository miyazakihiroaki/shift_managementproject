from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView
# from django.http import HttpResponse, HttpResponseRedirect

from .models import Userr
from .forms import UserCreationForm


#ログイン
class Login(LoginView):
    template_name = 'accounts/login.html'


        
#新規店員登録
def signup(request):
    context = {}
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            # messages.success(request, '新規会員登録が完了しました')
            return redirect('accounts:finish-signup')       
    return render(request, 'accounts/sigup.html', context)


# 新規登録完了画面
class FinishSignupView(TemplateView):
    template_name = 'accounts/finish_signup.html'


#店員一覧画面
class ListClerkView(ListView):
    template_name = 'accounts/clerk_list.html'
    model = Userr    

    
#店員詳細画面    
class DetailClerkView(DetailView):
    template_name = 'accounts/clerk_detail.html'
    model = Userr
    

#ログイン者の情報表示
def myinfo(request):
    myinfo_data = Userr.objects.get(id=request.user.id)
    context = {'myinfo_data':myinfo_data}
    return render(request, 'accounts/myinfo.html', context)
    




    
