from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.conf.urls.static import static
from django.conf import settings

from . import views

app_name = 'accounts'


urlpatterns = [
    path('login/', views.Login.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('signup/', views.signup, name="signup"),   
    path('myinfo/', views.myinfo, name="profile"),   
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),  
    path('clerklist/', views.ListClerkView.as_view(), name="clerklist"),
    path('clerklist/<int:pk>/detail/', views.DetailClerkView.as_view(), name="clerkdetail"),
    path('finish_signup', views.FinishSignupView.as_view(), name="finish-signup"),
    
    ##店長専用ページ
    path('manager_page/clerklist/', views.ListClerkView_Manager.as_view(), name="manager-clerklist"),
    
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)