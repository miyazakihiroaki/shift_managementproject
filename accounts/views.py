from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Userr
from .forms import UserCreationForm, ProfileForm


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
            return redirect('accounts:finish-signup')       
    return render(request, 'accounts/sigup.html', context)


# 新規登録完了画面
class FinishSignupView(TemplateView):
    template_name = 'accounts/finish_signup.html'


#店員一覧画面（スタッフ）
class ListClerkView(ListView):
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
            request.POST or None,
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
        form = ProfileForm(request.POST or None)
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
        
        return render(request, 'accounts/profile.html', context)
