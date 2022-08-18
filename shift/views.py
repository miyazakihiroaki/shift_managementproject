from datetime import datetime, date, time, timedelta
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

########################################################################################3
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
        
        #1時間当たりシフトに入る人数を取得
        staff_per_hour = Shop_info.objects.get().people_per_hour
        
        calendar = {}
        staff_number = []
        # 営業開始時刻～営業終了時刻
        for hour in range(store_start_time.hour, store_end_time.hour+1):
            
            if time(hour=hour, minute=0) <= store_end_time:
                hour_str = str(hour)
                if len(hour_str) == 1:
                    hour_str = "0" + hour_str
                minute_str = str(0)
                if minute_str == "0":
                    minute_str = "00"
                hour_minute = hour_str + ":" + minute_str
                row = {}
                for day in days:
                    row[day] = ""
                calendar[hour_minute] = row
                
        start_time = make_aware(datetime.combine(start_day, store_start_time))
        end_time = make_aware(datetime.combine(end_day, store_end_time))
        booking_data = staff_data.exclude(Q(workingtime__gt=end_time) | Q(workingtime__lt=start_time))
        for booking in booking_data:
            local_time = localtime(booking.workingtime)
            number = Shift.objects.filter(user = request.user).count()
            staff_number.append(number)
            booking_date = local_time.date()
            booking_hour = str(local_time.hour)
            booking_minute = str(local_time.minute)
            if booking_minute == "0":
                booking_minute = "00"
            booking_hour_minute = booking_hour + ":" + booking_minute
            if (booking_hour_minute in calendar) and (booking_date in calendar[booking_hour_minute]):
                calendar[booking_hour_minute][booking_date] = "???"
        
        context = {
            'staff_data': staff_data,
            'staff_name_data': staff_name_data,
            'people_per_hour': staff_per_hour,
            'staff_number':staff_number,
            'booking_data': booking_data,
            'calendar': calendar,
            'days': days,
            'start_day': start_day,
            'end_day': end_day,
            'before': days[0] - timedelta(days=7),
            'next': days[-1] + timedelta(days=1),
            'year': year,
            'month': month,
            'day': day,
            'store_start_time':store_start_time,
        }

        return render(request, 'shift/mypage.html',context )
        

@require_POST
def Holiday(request, year, month, day, hour_minute):
    staff_data = Shift.objects.filter(user=request.user)[0]
    booking_unit = 60
    hour = int(hour_minute[0:2])
    minute = int(hour_minute[3:5])
    start_time = make_aware(datetime(year=year, month=month, day=day, hour=hour, minute=minute))
    end_time = make_aware(datetime(year=year, month=month, day=day, hour=hour, minute=minute) + timedelta(minutes=booking_unit))

    # 勤務可能日追加
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

