from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from . import views

app_name = 'shift'


urlpatterns = [
    path('', views.index, name="index"),
    path('shop_info/', views.shop_info, name="shop_info"),
    
    #実験用
    path('test/', views.test, name="test"),
    
    ###################################################################柴田先生のコード参考
    # appのviewの30~38行目参考にしろ　ログイン後に仮のトップページを挟んで時刻を取得したら上手くいきそう
    #制限する　app views.py # 予約受付リミットを取得
    # deadline = date.today() + timedelta(days=30)
        # yesterday = date.today() - timedelta(days=1)
        # deadline = date.today() + timedelta(days=30)
        # deadline_time = (datetime.now() + timedelta(hours=timelimit.hour, minutes=timelimit.minute)).time()
        # if deadline_time > store_end_time:
        #     deadline_time = store_end_time
        # if end_rule == 0 and course_time >= 2:
        #     for count in range(1, course_time):
        #         target_time = (datetime.combine(today, store_end_time) - timedelta(minutes=booking_unit*count)).time()
        #         target_hour = str(target_time.hour)
        #         target_minute = str(target_time.minute)
        #         if target_minute == "0":
        #             target_minute = "00"
        #         target_hour_minute = target_hour + ":" + target_minute
        #         for day in days:
                    # calendar[target_hour_minute][day] = False
        # font-awesome　cssbootstrapの代わりみたいなもの
        # userrに店長か田舎のカテゴリーを表すモデルを追加しよう
    path('mypage/<int:year>/<int:month>/<int:day>/', views.MyPageView.as_view(), name='mypage'),
    path('mypage/holiday/<int:year>/<int:month>/<int:day>/<str:hour_minute>/', views.Holiday, name='holiday'),
    path('mypage/delete/<int:year>/<int:month>/<int:day>/<str:hour_minute>/', views.Delete, name='delete'),
    ###################################################################
]