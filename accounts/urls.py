from django.contrib.auth import views as auth_views
from django.urls import path, re_path
from django.contrib.auth.views import LoginView, LogoutView
from django.conf.urls.static import static
from django.conf import settings

from . import views

app_name = 'accounts'


urlpatterns = [
    path('login/', views.Login.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('signup/', views.signup, name="signup"),   
    path('profile/', views.myinfo, name="profile"), 
    path('profile/edit/<int:pk>/', views.UpdateProfileView.as_view(), name='profile_edit'),         
    path('clerklist/', views.ListClerkView.as_view(), name="clerklist"),
    path('clerklist/<int:pk>/detail/', views.DetailClerkView.as_view(), name="clerkdetail"),
    path('finish_signup', views.FinishSignupView.as_view(), name="finish-signup"),
    
    #パスワードリセット関係
    path('password_reset_form/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html', from_email='h12.miyazakihiroaki@gmail.com'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_mail_done.html'), name='password_reset_done'),
    path('password_reset/<str:uidb64>/<str:token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirmation.html'), name='password_reset_confirm'),
    path('password_reset_finish/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_finish.html'), name='password_reset_complete'),
    
    ##店長専用ページ
    path('manager_page/clerklist/', views.ListClerkView_Manager.as_view(), name="manager-clerklist"),    
]
