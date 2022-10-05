from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, DetailView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.core.mail import send_mail
from django.template.loader import render_to_string

import os 

from .models import Userr
from .forms import UserCreationForm, ProfileForm


#ログイン
class Login(LoginView):
    template_name = 'accounts/login.html'

        
#新規店員登録
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            email = str(form.cleaned_data['email'])
            clerkname = str(form.cleaned_data['clerkname'])
            user.save()
            context = {'email':email, 'clerkname': clerkname}
            print(context)
            
            # 題名（subject）：文字列
            # 本文（message）：文字列
            # 送信元アドレス（from_email）：文字列
            # 送信先アドレス（recipient_list）：リスト
            send_mail(
                    '新規登録完了のお知らせ',
                    render_to_string("accounts/mailers/finish_signup.txt", context),
                    os.getenv('DEFAULT_FROM_EMAIL'),
                    [email],
                    fail_silently=False,
                )
            
            return redirect('accounts:finish-signup')      
    return render(request, 'accounts/sigup.html')


# 新規登録完了画面
class FinishSignupView(TemplateView):
    template_name = 'accounts/finish_signup.html'


#店員一覧画面（スタッフ）
class ListClerkView(LoginRequiredMixin, ListView):
    template_name = 'accounts/clerk_list.html'
    model = Userr

    
#店員一覧画面（店長）
class ListClerkView_Manager(ListView):
    template_name = 'accounts/manager/clerk_list.html'
    model = Userr    

    
#店員詳細画面    
class DetailClerkView(DetailView):
    template_name = 'accounts/clerk_detail.html'
    model = Userr
    

#ログイン者の情報表示
@login_required
def myinfo(request):
    myinfo_data = Userr.objects.get(id=request.user.id)
    context = {'myinfo_data':myinfo_data}
    if request.user.category == 0:
        return render(request, 'accounts/profile.html', context)
    else:
        return render(request, 'accounts/manager/profile.html', context)

    
#登録情報更新    
class ProfileEditView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user_data = Userr.objects.get(id=request.user.id)
        form = ProfileForm(
            request.POST, request.FILES or None,
            initial={
                'clerkname': user_data.clerkname,
                'email': user_data.email,
                'introduction_text': user_data.introduction_text,
                'personalimage': user_data.personalimage,
            }
        )
        context = {'form': form, 'user_data': user_data}
        if user_data.category == 0:
            return render(request, 'accounts/profile_edit.html', context)
        else:
            return render(request, 'accounts/manager/profile_edit.html', context)

    def post(self, request, *args, **kwargs):
        user_data = Userr.objects.get(id=request.user.id)
        form = ProfileForm(request.POST,request.FILES)
        if form.is_valid():
            user_data = Userr.objects.get(id=request.user.id)
            user_data.clerkname = form.cleaned_data['clerkname']
            user_data.email = form.cleaned_data['email']  
            user_data.introduction_text = form.cleaned_data['introduction_text']
            user_data.personalimage = form.cleaned_data['personalimage']
            # return redirect('accounts:profile')
            context = {'myinfo_data':user_data}
            return render(request, 'accounts/profile.html', context)
            
            
        context = {'form':form}
        if user_data.category == 0:
            return render(request, 'accounts/profile.html', context)
        else:
            return render(request, 'accounts/manager/profile.html', context)


class UpdateProfileView(LoginRequiredMixin, UpdateView):
    model = Userr
    fields = ('clerkname', 'email', 'personalimage', 'introduction_text')
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')