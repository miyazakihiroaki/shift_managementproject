from datetime import datetime, date, time, timedelta, timezone
from django.utils.timezone import localtime, make_aware
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.generic import View
from django.urls import reverse, reverse_lazy

from accounts.models import Userr
from shift.models import Shop_info, Shift


def test(request):
    info = Shop_info.objects.get(pk=1)
    info_1 = info.start_workingtime
    
    # info_2 = Userr.objects.filter(clerkname=request.clerkname)[0]
    info_2 = Userr.objects.all()[0]
    x = info_2.clerkname
    
    info_3 = Shift.objects.first()
    y = info_3.user.clerkname
    
    info_5 = Shift.objects.filter(user=request.user)[1]
    # w = info_5.count()
    w = info_5.user.clerkname
    
    staff_name_data = Shift.objects.filter(user=request.user)[1]
    
    context = {'info_1':info_1, 'info':info, 'x':x, 'y': y, 'w':w, 'info_5':info_5,'staff_name_data':staff_name_data}
    return render(request, 'shift/test.html', context)

#トップページ練習用
def index(request):
    staff_data = Shift.objects.filter(user=request.user).first()
    context = {'object':staff_data}
    return render(request, 'shift/home.html', context)
    

#店舗詳細画面
def shop_info(request):
    info = Shop_info.objects.all().order_by('-id').first() # idカラム降順で並び替え
    context = {'object':info}
    return render(request, 'shift/shop_info.html', context)


#トップページに行く前に現在日時等を取得してカレンダーに渡す
class ReverseView(View):
    def get(self, request):
        
        if request.user.is_authenticated:
            user_data = Userr.objects.get(id=request.user.id)
            # user_data = Userr.objects.get(clerkname = request.user)なんでこれじゃダメなのか？？
            if self.request.user.category == 0:
                start_date = date.today()
                weekday = start_date.weekday()
                # カレンダー日曜日開始
                if weekday != 6:
                    start_date = start_date - timedelta(days=weekday + 1)
                return redirect('shift:mypage', start_date.year, start_date.month, start_date.day)
        else:
            user_data = None

        return render(request, 'shift/home.html')


#カレンダー関係
class MyPageView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        staff_data =Shift.objects.filter(user=request.user)
        staff_name_data = Shift.objects.filter(user=request.user).first()
        #urlから年月日を取得
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        start_date = date(year=year, month=month, day=day)
        days = [start_date + timedelta(days=day) for day in range(7)]
        start_day = days[0]
        end_day = days[-1]
        
        #店舗営業時間取得
        store_start_time = Shop_info.objects.get(pk=1).start_workingtime
        store_end_time =Shop_info.objects.get(pk=1).finish_workingtime
        
        limit = Shop_info.objects.get(pk=1).deadline_day
        
        #1時間当たりシフトに入る人数を取得
        staff_per_hour = Shop_info.objects.get().people_per_hour
        
        calendar1 = {}#全体集計用
        calendar2 = {}#各個人（ログインユーザー）集計用
        
        # 営業開始時刻～営業終了時刻までのカレンダー作成
        for hour in range(store_start_time.hour, store_end_time.hour+1):
            
            if time(hour=hour, minute=0) <= store_end_time:
                hour_str = str(hour)
                if len(hour_str) == 1:
                    hour_str = "0" + hour_str
                minute_str = str(0)
                if minute_str == "0":
                    minute_str = "00"
                hour_minute = hour_str + ":" + minute_str
                row1 = {}
                row2 = {}
                calendar1[hour_minute] = row1
                calendar2[hour_minute] = row2
                for day_k in days:
                    row1[day_k] = ""
                for day_k in days:
                    row2[day_k] = ""
                    deadline_time = (datetime(year=year, month=month, day=int(day_k.day), hour=hour, minute=0) + timedelta(days=-limit))
                    if deadline_time < datetime.now():
                        calendar2[hour_minute][day_k] = "False"                                    
                
        start_time = make_aware(datetime.combine(start_day, store_start_time))
        end_time = make_aware(datetime.combine(end_day, store_end_time))
        booking_data1 = Shift.objects.exclude(Q(workingtime__gt=end_time) | Q(workingtime__lt=start_time))#全体集計用
        booking_data2 = staff_data.exclude(Q(workingtime__gt=end_time) | Q(workingtime__lt=start_time))#各個人集計用
        
        
        for booking in booking_data2:
            local_time = localtime(booking.workingtime)
            booking_date = local_time.date()
            booking_hour = str(local_time.hour)
            if len(booking_hour) == 1:
                    booking_hour = "0" + booking_hour
            booking_minute = str(local_time.minute)
            if booking_minute == "0":
                booking_minute = "00"
            booking_hour_minute = booking_hour + ":" + booking_minute            
            if (booking_hour_minute in calendar2) and (booking_date in calendar2[booking_hour_minute]) and calendar2[booking_hour_minute][booking_date] != "False":
                calendar2[booking_hour_minute][booking_date] = "出勤"
        
        for booking in booking_data1:
            local_time = localtime(booking.workingtime)
            number = Shift.objects.filter(workingtime = local_time).count()
            booking_date = local_time.date()
            booking_hour = str(local_time.hour)
            if len(booking_hour) == 1:
                    booking_hour = "0" + booking_hour
            booking_minute = str(local_time.minute)
            if booking_minute == "0":
                booking_minute = "00"
            booking_hour_minute = booking_hour + ":" + booking_minute
            calendar1[booking_hour_minute][booking_date] = str(number)
            if int(calendar1[booking_hour_minute][booking_date]) >= int(staff_per_hour):
                calendar1[booking_hour_minute][booking_date] = "既定人数到達" 
                calendar2[booking_hour_minute][booking_date] = "既定人数到達" 
            
        # for booking in booking_data:
        #     local_time = localtime(booking.workingtime)
        #     # number = Shift.objects.filter(user = request.user, workingtime = local_time).count()
        #     number = Shift.objects.filter(workingtime = local_time).count()
        #     booking_date = local_time.date()
        #     booking_hour = str(local_time.hour)
        #     if len(booking_hour) == 1:
        #             booking_hour = "0" + booking_hour
        #     booking_minute = str(local_time.minute)
        #     if booking_minute == "0":
        #         booking_minute = "00"
        #     booking_hour_minute = booking_hour + ":" + booking_minute
        #     # if (booking_hour_minute in calendar) and (booking_date in calendar[booking_hour_minute]):
        #         # calendar[booking_hour_minute][booking_date] = str(number)
        #     calendar[booking_hour_minute][booking_date] = str(number)
        #     if calendar[booking_hour_minute][booking_date] >= str(staff_per_hour):
        #         calendar[booking_hour_minute][booking_date] = "既定人数到達"                
                
        
        context = {
            'staff_data': staff_data,
            'staff_name_data': staff_name_data,
            'people_per_hour': staff_per_hour,
            'booking_data1': booking_data1,
            'calendar1': calendar1,
            'calendar2': calendar2,
            'days': days,
            'start_day': start_day,
            'end_day': end_day,
            'before': days[0] - timedelta(days=7),
            'next': days[-1] + timedelta(days=1),
            'next_month': days[0] + timedelta(days=30),
            'before_month': days[0] - timedelta(days=30),
            'year': year,
            'month': month,
            'day': day,
            'store_start_time':store_start_time,
        }

        return render(request, 'shift/mypage.html',context )
        

#出勤時間登録
@require_POST
def Holiday(request, year, month, day, hour_minute):
    staff_data = Shift.objects.filter(user=request.user)[0]
    booking_unit = 60
    hour = int(hour_minute[0:2])
    minute = int(hour_minute[3:5])
    start_time = make_aware(datetime(year=year, month=month, day=day, hour=hour, minute=minute))
    end_time = make_aware(datetime(year=year, month=month, day=day, hour=hour, minute=minute) + timedelta(minutes=booking_unit))

    # 出勤時間をShiftモデルに追加
    Shift.objects.create(
        user = staff_data.user,
        workingtime=start_time,
    )

    start_date = date(year=year, month=month, day=day)
    weekday = start_date.weekday()
    # カレンダー日曜日開始
    if weekday != 6:
        start_date = start_date - timedelta(days=weekday + 1)
    return redirect('shift:mypage', year=start_date.year, month=start_date.month, day=start_date.day)


#出勤時間消去
@require_POST
def Delete(request, year, month, day, hour_minute):
    hour = int(hour_minute[0:2])
    minute = int(hour_minute[3:5])
    start_time = make_aware(datetime(year=year, month=month, day=day, hour=hour, minute=minute))
    booking_data = Shift.objects.filter(user=request.user)
    booking_data =booking_data.filter(workingtime=start_time)

    # シフト削除
    booking_data.delete()

    start_date = date(year=year, month=month, day=day)
    weekday = start_date.weekday()
    # カレンダー日曜日開始
    if weekday != 6:
        start_date = start_date - timedelta(days=weekday + 1)
    return redirect('shift:mypage', year=start_date.year, month=start_date.month, day=start_date.day)

