from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from . import views

app_name = 'accounts'


urlpatterns = [
    path('login/', views.Login.as_view(), name="login"),
    # path('login_redirect/', views.login_redirect, name='login_redirect'), # login_redirect 時に実行されるurl,view関数
    path('logout/', LogoutView.as_view(), name="logout"),
    path('signup/', views.signup, name="signup"),   
    path('clerklist/', views.ListClerkView.as_view(), name="clerklist"),
    path('clerklist/<int:pk>/detail/', views.DetailClerkView.as_view(), name="clerkdetail"),
    path('finish_signup', views.FinishSignupView.as_view(), name="finish-signup"),
    
]
