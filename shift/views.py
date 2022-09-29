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

#店舗固有情報取得
store_start_time = Shop_info.objects.get(pk=1).start_workingtime
store_end_time =Shop_info.objects.get(pk=1).finish_workingtime        
limit = Shop_info.objects.get(pk=1).deadline_day
staff_per_hour = Shop_info.objects.get().people_per_hour
now = datetime.now()

def get_path(request):
    path = request.path #ドメインを含まないフルパス
    # path_2 = request.get_full_path() # クエリパラメーターを含むパス
    # path_3 = request.build_absolute_uri() #ドメインを含むパス
    return path

class Login(LoginView):
    template_name = 'accounts/login.html'
    
    
#店舗詳細画面
def shop_info(request):
    shop_info = Shop_info.objects.all().order_by('-id').first() # idカラム降順で並び替え
    context = {
        'object':shop_info
    }
    
    if request.user.category == 0:
        return render(request, 'shift/shop_info.html', context)
    else:
        return render(request, 'shift/manager/shop_info.html', context)
        

#トップページに行く前に現在日時等を取得してカレンダーに渡す
class ReverseView(View):
    
    def get(self, request):       
        if request.user.is_authenticated:
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
        
        all_staff_calender = {}#全体集計用
        staff_calender = {}#各個人（ログインユーザー）集計用
        
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
                all_staff_calender[hour_minute] = row1
                staff_calender[hour_minute] = row2
                # 個人用
                for day_k in days:
                    row2[day_k] = {}
                    deadline_time = (datetime(year=int(day_k.year), month=int(day_k.month), day=int(day_k.day), hour=hour, minute=0) + timedelta(days = -limit))
                    staff_calender[hour_minute][day_k]["attend"] =""
                    staff_calender[hour_minute][day_k]["is_max"] =""
                    # リミット以前の日時にFALSE
                    if deadline_time < datetime.now():
                            staff_calender[hour_minute][day_k]["attend"] = "false"                                   
                
                #全体用
                for day_k in days:
                    row1[day_k] = ""
                    number = Shift.objects.filter(workingtime = datetime(year=int(day_k.year), month=int(day_k.month), day=int(day_k.day), hour=hour, minute=0)).count()
                    all_staff_calender[hour_minute][day_k] = number
                    if int(all_staff_calender[hour_minute][day_k]) == int(staff_per_hour):
                        all_staff_calender[hour_minute][day_k] = "既定人数到達" 
                        # スタッフ数が規定人数に到達した際の処理
                        staff_calender[hour_minute][day_k]["is_max"] = "既定人数到達" 
                    
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
            if (booking_hour_minute in staff_calender) and (booking_date in staff_calender[booking_hour_minute]) and staff_calender[booking_hour_minute][booking_date]["attend"] != "false":
                staff_calender[booking_hour_minute][booking_date]["attend"] = "出勤"
        
        context = {
            'staff_data': staff_data,
            'staff_name_data': staff_name_data,
            'staff_name_datas':staff_name_datas,
            'people_per_hour': staff_per_hour,
            'booking_data1': booking_data1,
            'calendar1': all_staff_calender,
            'calendar2': staff_calender,
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
        }
        
        if self.request.user.category == 0:
            return render(request, 'shift/mypage.html',context )
        

#出勤時間登録
@require_POST
def Holiday(request, year, month, day, hour_minute):
    staff_name_data = Userr.objects.get(id=request.user.id)
    hour = int(hour_minute[0:2])
    minute = int(hour_minute[3:5])
    start_time = make_aware(datetime(year=year, month=month, day=day, hour=hour, minute=minute))
    
    # 出勤時間をShiftモデルに追加
    Shift.objects.create(
        user = staff_name_data,
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


#給料計算
class CalculateSalary(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        
        #urlから年月を取得
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        
        #日時処理
        next_year = year
        before_year = year
        next_month = month + 1
        if next_month == 13:
            next_month = 1
            next_year = year + 1
        before_month = month - 1
        if before_month== 0:
            before_month = 12
            before_year = year - 1
        next_date = date(year=next_year, month=next_month, day = 1)
        before_date = date(year=before_year, month=before_month, day = 1)
        
        #データ検索
        user = self.request.user
        month_query = str(month)
        if len(month_query) == 1:
            month_query = "0" + month_query
            
        shifts = Shift.objects.filter(user_id = user.id, workingtime__contains = f"{year}-{month_query}-")
        shifts_count = shifts.count()
        salary = shifts_count*user.hourly_wage
        
        context = {
            'year':year,
            'month':month,
            'shifts': shifts,
            'shifts_count': shifts_count, 
            'salary':salary, 
            'next_date': next_date,
            'before_date': before_date
        }
        
        return render(request, 'shift/calculatesalary.html',context)


#給料取得前に現在年月を取得してカレンダーに渡す
class SalaryReverseView(View):
    def get(self, request):
        
        if request.user.is_authenticated:
            user_data = Userr.objects.get(id=request.user.id)
            if self.request.user.category == 0:
                start_date = date.today()
                start_date = start_date + timedelta(days=28)
                weekday = start_date.weekday()
                # カレンダー日曜日開始
                if weekday != 6:
                    start_date = start_date - timedelta(days=weekday + 1)
                return redirect('shift:calculate_salary', start_date.year, start_date.month)
    
        else:
            user_data = None

        return render(request, 'shift/home.html') 
    
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

        deadline_time = (datetime(year=year, month=month, day=day, hour=6, minute=0) + timedelta(days = -limit))
        
        # 背景色の不透明度リストを格納
        opacity_list = [75,50,25,10, 0]
        all_staff_calender = {}#全体集計用
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
                all_staff_calender[hour_minute] = row1
                for day_k in days:
                    row1[day_k] = {}
                    number = Shift.objects.filter(workingtime = datetime(year=int(day_k.year), month=int(day_k.month), day=int(day_k.day), hour=hour, minute=0)).count()
                    all_staff_calender[hour_minute][day_k]["number"] = number
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
                        all_staff_calender[hour_minute][day_k]["opacity"] = opacity_list[2]
                    else:
                        all_staff_calender[hour_minute][day_k]["opacity"] = opacity_list[4]    
                    #規定人数到達の確認
                    if int(all_staff_calender[hour_minute][day_k]["number"]) >= int(staff_per_hour):
                        all_staff_calender[hour_minute][day_k]["number"] = "既定人数到達"     
                        
        start_time = make_aware(datetime.combine(start_day, store_start_time))
        end_time = make_aware(datetime.combine(end_day, store_end_time))
        booking_data1 = Shift.objects.exclude(Q(workingtime__gt=end_time) | Q(workingtime__lt=start_time))#全体集計用
        
        context = {
            'people_per_hour': staff_per_hour,
            'booking_data1': booking_data1,
            'calendar1': all_staff_calender,
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
    context = {
        'booking_data':booking_data, 
        'start_time':start_time,
        'form':form
    }
    
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

        all_staff_calender = {}#全体集計用
        staff_calender = {}#各個人（ログインユーザー）集計用

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
                all_staff_calender[hour_minute] = row1
                staff_calender[hour_minute] = row2
                # 個人用
                for day_k in days:
                    row2[day_k] = {}
                    deadline_time = (datetime(year=int(day_k.year), month=int(day_k.month), day=int(day_k.day), hour=hour, minute=0) + timedelta(days = -limit))
                    staff_calender[hour_minute][day_k]["attend"] =""
                    staff_calender[hour_minute][day_k]["is_max"] =""
                    staff_calender[hour_minute][day_k]["is_valid"] =""
                    # リミット以前の日時にFALSE
                    if deadline_time < datetime.now():
                            staff_calender[hour_minute][day_k]["is_valid"] = "false"                                   
                
                #全体用
                for day_k in days:
                    row1[day_k] = ""
                    number = Shift.objects.filter(workingtime = datetime(year=int(day_k.year), month=int(day_k.month), day=int(day_k.day), hour=hour, minute=0)).count()
                    all_staff_calender[hour_minute][day_k] = number
                    if int(all_staff_calender[hour_minute][day_k]) >= int(staff_per_hour):
                        all_staff_calender[hour_minute][day_k] = "既定人数到達" 
                        # スタッフ数が規定人数に到達した際の処理
                        staff_calender[hour_minute][day_k]["is_max"] = "既定人数到達" 
                    
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
            if (booking_hour_minute in staff_calender) and (booking_date in staff_calender[booking_hour_minute]) and staff_calender[booking_hour_minute][booking_date]["attend"] != "false":
                staff_calender[booking_hour_minute][booking_date]["attend"] = "出勤"
        
        context = {
            'staff_id':staff_id,
            'staff_data': staff_data,
            'staff_name_data':staff_name_data,
            'people_per_hour': staff_per_hour,
            'booking_data2': booking_data2,
            'calendar2': staff_calender,
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
        }
        path = get_path(request)
        if "view_only" in path:
            if self.request.user.category == 1:
                return render(request, 'shift/manager_detail_mypage_view_only.html',context )
            else:
                return render(request, 'shift/shift_view_only.html',context )                
        
        else:
            return render(request, 'shift/manager_detail_mypage.html',context )                


def select_staff(request):
    staff_data = Userr.objects.get(id=request.user.id)
    staff_name_datas = Userr.objects.all()
    context = {
        'staff_name_datas':staff_name_datas
    }
    
    if staff_data.category == 1:
        return render(request, 'shift/manager_select_staff.html', context)
    else :
        return render(request, 'shift/select_staff.html', context)
        


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
            if self.request.user.category == 1:
                return redirect('shift:manager_staff_shift_view_only', id, start_date.year, start_date.month, start_date.day)            
            else:    
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
    shift_data = Shift.objects.filter(user=staff_data.user, workingtime=start_time)
    
    # シフト削除
    shift_data.delete()

    start_date = date(year=year, month=month, day=day)
    weekday = start_date.weekday()
    # カレンダー日曜日開始
    if weekday != 6:
        start_date = start_date - timedelta(days=weekday + 1)
    return redirect('shift:staff_shift', pk, start_date.year, start_date.month, start_date.day)