from datetime import datetime, date, time, timedelta, timezone
from django.utils.timezone import localtime, make_aware
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.views import LoginView
from django.urls import reverse, reverse_lazy

from accounts.models import Userr
from shift.models import Shop_info, Shift
from shift.forms import StaffSelectForm

def get_path(request):
    path = request.path #ドメインを含まないフルパス
    # path_2 = request.get_full_path() # クエリパラメーターを含むパス
    # path_3 = request.build_absolute_uri() #ドメインを含むパス
    return path

class Login(LoginView):
    template_name = 'accounts/login.html'

def test(request):
    info = Shop_info.objects.get(pk=1)
    info_1 = info.start_workingtime
    
    # info_2 = Userr.objects.filter(clerkname=request.clerkname)[0]
    info_2 = Userr.objects.all()[0]
    x = info_2.clerkname
    
    info_3 = Shift.objects.first()
    y = info_3.user.clerkname
    
    
    
    # staff_name_data = Shift.objects.filter(user=request.user)[1]
    staff_name_data = Userr.objects.get(id=2)
    staff_name_data = staff_name_data.clerkname
    staff_data =Shift.objects.filter(user_id = 1)
    
    context = {'info_1':info_1, 'info':info, 'x':x, 'y': y, 'staff_data':staff_data, 'staff_name_data':staff_name_data}
    return render(request, 'shift/test.html', context)

#トップページ練習用
def index(request):
    if request.user.is_authenticated:
        staff_data = Shift.objects.filter(user=request.user).first()
        opacity_list = [75,50,25,10]
        opacity = {'75': 75, '50': 50, '25': 25, '10': 10}
        context = {'object':staff_data, 'opacity_list': opacity_list, 'opacity' : opacity}
        print(opacity_list[0])
        print(opacity['75'])
        return render(request, 'shift/home.html', context)
    else:
        print("User is not logged in")
    return render(request, 'accounts/no_login.html')
    

#店舗詳細画面
def shop_info(request):
    info = Shop_info.objects.all().order_by('-id').first() # idカラム降順で並び替え
    context = {'object':info}
    if request.user.category == 0:
        return render(request, 'shift/shop_info.html', context)
    else:
        return render(request, 'shift/manager/shop_info.html', context)
        


#トップページに行く前に現在日時等を取得してカレンダーに渡す
class ReverseView(View):
    def get(self, request):
        
        if request.user.is_authenticated:
            user_data = Userr.objects.get(id=request.user.id)
            # user_data = Userr.objects.get(clerkname = request.user)なんでこれじゃダメなのか？？
            if self.request.user.category == 0:
                start_date = date.today()
                start_date = start_date + timedelta(days=28)
                weekday = start_date.weekday()
                # カレンダー日曜日開始
                if weekday != 6:
                    start_date = start_date - timedelta(days=weekday + 1)
                return redirect('shift:mypage', start_date.year, start_date.month, start_date.day)
            
            elif self.request.user.category == 1:
                start_date = date.today()
                start_date = start_date
                weekday = start_date.weekday()
                # カレンダー日曜日開始
                if weekday != 6:
                    start_date = start_date - timedelta(days=weekday + 1)
                return redirect('shift:manager_page', start_date.year, start_date.month, start_date.day)
    
        else:
            user_data = None

        return render(request, 'shift/home.html')


#カレンダー関係
class MyPageView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        staff_data =Shift.objects.filter(user=request.user)
        staff_name_data = Userr.objects.get(id=request.user.id)
        staff_name_datas = Userr.objects.all()
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
        now = datetime.now()
        deadline_time = (datetime(year=year, month=month, day=day, hour=6, minute=0) + timedelta(days = -limit))
        
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
                    number = Shift.objects.filter(workingtime = datetime(year=int(day_k.year), month=int(day_k.month), day=int(day_k.day), hour=hour, minute=0)).count()
                    calendar1[hour_minute][day_k] = number
                    if int(calendar1[hour_minute][day_k]) == int(staff_per_hour):
                        calendar1[hour_minute][day_k] = "既定人数到達" 
                        calendar2[hour_minute][day_k] = "既定人数到達" 
                for day_k in days:
                    row2[day_k] = ""
                    deadline_time = (datetime(year=int(day_k.year), month=int(day_k.month), day=int(day_k.day), hour=hour, minute=0) + timedelta(days = -limit))
                    if deadline_time < datetime.now() and calendar2[hour_minute][day_k] != "既定人数到達":
                        calendar2[hour_minute][day_k] = "False"                                    
                
        start_time = make_aware(datetime.combine(start_day, store_start_time))
        end_time = make_aware(datetime.combine(end_day, store_end_time))
        booking_data1 = Shift.objects.exclude(Q(workingtime__gt=end_time) | Q(workingtime__lt=start_time))#全体集計用
        booking_data2 = staff_data.exclude(Q(workingtime__gt=end_time) | Q(workingtime__lt=start_time))#各個人集計用
        
        
        # for booking in booking_data2:
        for booking in staff_data:
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
                print(f"booking_hour_minuteは{booking_hour_minute}で\nbooking_dateは{booking_date}です")
                calendar2[booking_hour_minute][booking_date] = "出勤"
        
        # for booking in booking_data1:
        #     local_time = localtime(booking.workingtime)
        #     booking_date = local_time.date()
        #     booking_hour = str(local_time.hour)
        #     if len(booking_hour) == 1:
        #             booking_hour = "0" + booking_hour
        #     booking_minute = str(local_time.minute)
        #     if booking_minute == "0":
        #         booking_minute = "00"
        #     booking_hour_minute = booking_hour + ":" + booking_minute
        
        # 背景色の不透明度リストを格納
        opacity_list = [75,50,15,20]
        
        context = {
            'staff_data': staff_data,
            'staff_name_data': staff_name_data,
            'staff_name_datas':staff_name_datas,
            'people_per_hour': staff_per_hour,
            'booking_data1': booking_data1,
            'calendar1': calendar1,
            'calendar2': calendar2,
            'days': days,
            'start_day': start_day,
            'end_day': end_day,
            'before': days[0] - timedelta(days=7),
            'next': days[-1] + timedelta(days=1),
            'next_month': days[0] + timedelta(days=28),
            'before_month': days[0] - timedelta(days=28),
            'year': year,
            'month': month,
            'day': day,
            'store_start_time':store_start_time,
            'now': now,
            'deadline_time':deadline_time,
        }
        if self.request.user.category == 0:
            return render(request, 'shift/mypage.html',context )
        

#出勤時間登録
@require_POST
def Holiday(request, year, month, day, hour_minute):
    staff_data = Shift.objects.filter(user=request.user).first()
    staff_name_data = Userr.objects.get(id=request.user.id)
    hour = int(hour_minute[0:2])
    minute = int(hour_minute[3:5])
    start_time = make_aware(datetime(year=year, month=month, day=day, hour=hour, minute=minute))
    
    # 出勤時間をShiftモデルに追加
    Shift.objects.create(
        user = staff_name_data,
        # user = staff_data.user,
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

# 店長専用
###########################################################################################################
class ManagerPageView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        #urlから取得
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        start_date = date(year=year, month=month, day=day)
        days = [start_date + timedelta(days=day) for day in range(7)]
        start_day = days[0]
        end_day = days[-1]
        
        
        #店舗情報取得
        store_start_time = Shop_info.objects.get(pk=1).start_workingtime
        store_end_time =Shop_info.objects.get(pk=1).finish_workingtime
        limit = Shop_info.objects.get(pk=1).deadline_day
        staff_per_hour = Shop_info.objects.get().people_per_hour

        deadline_time = (datetime(year=year, month=month, day=day, hour=6, minute=0) + timedelta(days = -limit))
        
        # 背景色の不透明度リストを格納
        opacity_list = [75,50,25,10, 0]
        calendar1 = {}#全体集計用
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
                calendar1[hour_minute] = row1
                for day_k in days:
                    row1[day_k] = {}
                    number = Shift.objects.filter(workingtime = datetime(year=int(day_k.year), month=int(day_k.month), day=int(day_k.day), hour=hour, minute=0)).count()
                    calendar1[hour_minute][day_k]["number"] = number
                    # #不透明度決定
                    # if number/staff_per_hour < 0.4:
                    #     calendar1[hour_minute][day_k]["opacity"] = opacity_list[0]
                    # elif number/staff_per_hour < 0.6:
                    #     calendar1[hour_minute][day_k]["opacity"] = opacity_list[1]
                    # elif number/staff_per_hour < 0.8:
                    #     calendar1[hour_minute][day_k]["opacity"] = opacity_list[2]
                    # else:
                    #     calendar1[hour_minute][day_k]["opacity"] = opacity_list[3]
                    
                    if number/staff_per_hour < 0.5:
                        calendar1[hour_minute][day_k]["opacity"] = opacity_list[2]
                    else:
                        calendar1[hour_minute][day_k]["opacity"] = opacity_list[4]    
                    #規定人数到達の確認
                    if int(calendar1[hour_minute][day_k]["number"]) == int(staff_per_hour):
                        calendar1[hour_minute][day_k]["number"] = "既定人数到達"     
                        
        start_time = make_aware(datetime.combine(start_day, store_start_time))
        end_time = make_aware(datetime.combine(end_day, store_end_time))
        booking_data1 = Shift.objects.exclude(Q(workingtime__gt=end_time) | Q(workingtime__lt=start_time))#全体集計用
        
        for booking in booking_data1:
            local_time = localtime(booking.workingtime)
            booking_date = local_time.date()
            booking_hour = str(local_time.hour)
            if len(booking_hour) == 1:
                    booking_hour = "0" + booking_hour
            booking_minute = str(local_time.minute)
            if booking_minute == "0":
                booking_minute = "00"
            booking_hour_minute = booking_hour + ":" + booking_minute
        
        context = {
            'people_per_hour': staff_per_hour,
            'booking_data1': booking_data1,
            'calendar1': calendar1,
            'days': days,
            'start_day': start_day,
            'end_day': end_day,
            'before': days[0] - timedelta(days=7),
            'next': days[-1] + timedelta(days=1),
            'next_month': days[0] + timedelta(days=28),
            'before_month': days[0] - timedelta(days=28),
            'year': year,
            'month': month,
            'day': day,
            'store_start_time':store_start_time,
            'deadline_time':deadline_time,
        }
        # print(calendar1)
        return render(request, 'shift/manager_mypage.html',context )
        
def shift_detail(request, year, month, day, hour_minute):
    hour = int(hour_minute[0:2])
    minute = int(hour_minute[3:5])
    start_time = make_aware(datetime(year=year, month=month, day=day, hour=hour, minute=minute))
    booking_data =Shift.objects.filter(workingtime=start_time)
    form = StaffSelectForm(request.POST)
    context = {'booking_data':booking_data, 'start_time':start_time, 'form':form,}
    
    return render(request, 'shift/shift_detail.html',context )


class Staff_Shift(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        #urlから取得
        staff_id = self.kwargs.get('pk')
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        start_date = date(year=year, month=month, day=day)
        days = [start_date + timedelta(days=day) for day in range(7)]
        start_day = days[0]
        end_day = days[-1]
        
        staff_data = Shift.objects.filter(user_id=staff_id)
        staff_name_data = Userr.objects.get(id=staff_id)
        staff_name_data = staff_name_data.clerkname
        
        #店舗営業時間取得
        store_start_time = Shop_info.objects.get(pk=1).start_workingtime
        store_end_time =Shop_info.objects.get(pk=1).finish_workingtime
        
        limit = Shop_info.objects.get(pk=1).deadline_day
        
        #1時間当たりシフトに入る人数を取得
        staff_per_hour = Shop_info.objects.get().people_per_hour

        calendar2 = {}#各個人（ログインユーザー）集計用
        deadline_time = (datetime(year=year, month=month, day=day, hour=6, minute=0) + timedelta(days = -limit))
        
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
                row2 = {}
                calendar2[hour_minute] = row2

                for day_k in days:
                    row2[day_k] = ""
                    deadline_time = (datetime(year=int(day_k.year), month=int(day_k.month), day=int(day_k.day), hour=hour, minute=0) + timedelta(days = -limit))
                    if deadline_time < datetime.now() and calendar2[hour_minute][day_k] != "既定人数到達":
                        calendar2[hour_minute][day_k] = "False"                                    
                
        start_time = make_aware(datetime.combine(start_day, store_start_time))
        end_time = make_aware(datetime.combine(end_day, store_end_time))
        booking_data1 = Shift.objects.exclude(Q(workingtime__gt=end_time) | Q(workingtime__lt=start_time))#全体集計用
        booking_data2 = staff_data.exclude(Q(workingtime__gt=end_time) | Q(workingtime__lt=start_time))#各個人集計用
        
        
        for booking in staff_data:
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
            booking_date = local_time.date()
            booking_hour = str(local_time.hour)
            if len(booking_hour) == 1:
                    booking_hour = "0" + booking_hour
            booking_minute = str(local_time.minute)
            if booking_minute == "0":
                booking_minute = "00"
            booking_hour_minute = booking_hour + ":" + booking_minute
        
        context = {
            'staff_id':staff_id,
            'staff_data': staff_data,
            'staff_name_data':staff_name_data,
            'people_per_hour': staff_per_hour,
            'booking_data2': booking_data2,
            'calendar2': calendar2,
            'days': days,
            'start_day': start_day,
            'end_day': end_day,
            'before': days[0] - timedelta(days=7),
            'next': days[-1] + timedelta(days=1),
            'next_month': days[0] + timedelta(days=28),
            'before_month': days[0] - timedelta(days=28),
            'year': year,
            'month': month,
            'day': day,
            'store_start_time':store_start_time,
            'deadline_time':deadline_time,
        }
        path = get_path(request)
        # if self.request.user.category == 1:
        if "view_only" in path:
            return render(request, 'shift/manager_detail_mypage_view_only.html',context )
        else:
            return render(request, 'shift/manager_detail_mypage.html',context )


def select_staff(request):
    staff_name_datas = Userr.objects.all()
    context = {'staff_name_datas':staff_name_datas}
    return render(request, 'shift/manager_select_staff.html', context)


class StaffReverseView(View):
    def get(self, request, *args, **kwargs):
        #urlからスタッフidを取得
        id = self.kwargs.get('pk')
        start_date = date.today()
        start_date = start_date + timedelta(days=28)
        weekday = start_date.weekday()
        # カレンダー日曜日開始
        if weekday != 6:
            start_date = start_date - timedelta(days=weekday + 1)
            return redirect('shift:staff_shift_view_only', id, start_date.year, start_date.month, start_date.day)

        return render(request, 'shift/home.html')
    

@require_POST
def Manager_Holiday(request, pk, year, month, day, hour_minute):
    staff_data = Shift.objects.filter(user_id = pk).first()
    hour = int(hour_minute[0:2])
    minute = int(hour_minute[3:5])
    start_time = make_aware(datetime(year=year, month=month, day=day, hour=hour, minute=minute))
    
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
    return redirect('shift:staff_shift', pk , start_date.year, start_date.month, start_date.day)


@require_POST
def Manager_Delete(request, pk, year, month, day, hour_minute):
    staff_data = Shift.objects.filter(user_id = pk).first()
    hour = int(hour_minute[0:2])
    minute = int(hour_minute[3:5])
    start_time = make_aware(datetime(year=year, month=month, day=day, hour=hour, minute=minute))
    booking_data = Shift.objects.filter(user=staff_data.user)
    booking_data =booking_data.filter(workingtime=start_time)
    # シフト削除
    booking_data.delete()

    start_date = date(year=year, month=month, day=day)
    weekday = start_date.weekday()
    # カレンダー日曜日開始
    if weekday != 6:
        start_date = start_date - timedelta(days=weekday + 1)
    return redirect('shift:staff_shift', pk, start_date.year, start_date.month, start_date.day)