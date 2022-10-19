from django.core.management.base import BaseCommand, CommandError
from datetime import datetime, date, timedelta, time
from django.db.models import Q
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.timezone import localtime, make_aware
from datetime import datetime, date, time, timedelta, timezone
from django.utils.timezone import localtime, make_aware
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.generic import View

from accounts.models import Userr
from shift.models import Shift

import os

class Command(BaseCommand):
    help = 'リマインダーメール送信'

    def handle(self, *args, **options):
        today = make_aware(datetime.now().replace(hour=0,minute=0,second=0,microsecond=0))
        tomorrow_0 = today + timedelta(days=1) #翌日0時
        tomorrow_24 = today + timedelta(days=2) #翌々日0時
        # 開始日時が翌日0時～翌々日0時のシフトを抽出
        
        #店員リストを取得
        users = Userr.objects.all()
        clerkname_id_list = []
        for user in users:
            clerkname_id = user.id
            clerkname_id_list.append(clerkname_id)
        shift_data = Shift.objects.filter(Q(start__gt=tomorrow_0) & Q(start__lt=tomorrow_24))

        all_shift_datas = Shift.objects.filter(Q(workingtime__gt=tomorrow_0) & Q(workingtime__lt=tomorrow_24))
        # リマインダーメール送信
        if all_shift_datas.exists():
            for clerkname_id in clerkname_id_list:
                shift_datas = all_shift_datas.filter(user_id = clerkname_id)
                if shift_datas.exists():
                    clerkname = shift_datas.first().user.clerkname
                    email = shift_datas.first().user.email
                    context = {'shift_datas': shift_datas, 'clerkname': clerkname}                
                    send_mail(
                        '明日の出勤のリマインド',
                        render_to_string("accounts/mailers/shift_remind.txt", context),
                        os.getenv('DEFAULT_FROM_EMAIL'),
                        [email],
                        fail_silently=False,
                    )      
        return