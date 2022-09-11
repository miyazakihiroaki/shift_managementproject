from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from . import views

app_name = 'shift'


urlpatterns = [
    path('', views.index, name="index"),
    path('reserve/', views.ReverseView.as_view(), name='reverse'),
    path('shop_info/', views.shop_info, name="shop_info"),
    
    #実験用
    path('test/', views.test, name="test"),
    
    ###################################################################柴田先生のコード参考    
    path('mypage/<int:year>/<int:month>/<int:day>/', views.MyPageView.as_view(), name='mypage'),
    path('mypage/holiday/<int:year>/<int:month>/<int:day>/<str:hour_minute>/', views.Holiday, name='holiday'),
    path('mypage/delete/<int:year>/<int:month>/<int:day>/<str:hour_minute>/', views.Delete, name='delete'),
    ###################################################################
    
    #店長専用ページ
    path('manager_page/<int:year>/<int:month>/<int:day>/',views.MyPageView.as_view(), name ='manager_page'),
    path('manager_page/shift_detail/<int:year>/<int:month>/<int:day>/<str:hour_minute>/',views.shift_detail, name ='shift_detail'),
    path('manager_page/staff_shift/<int:pk>/<int:year>/<int:month>/<int:day>/',views.Staff_Shift.as_view(), name ='staff_shift'),
]