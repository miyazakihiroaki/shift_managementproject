from datetime import datetime, date, timedelta, time
from django.db import models
from django.utils import timezone

from accounts.models import Userr


# 店舗情報
class Shop_info(models.Model):
    start_workingtime = models.TimeField('始業時刻', default=time(hour=9, minute=0), blank=True)
    finish_workingtime = models.TimeField('閉店時刻', default=time(hour=21, minute=0), blank=True)
    people_per_hour = models.IntegerField(default=5)
    deadline_day = models.IntegerField(default=30)
    email = models.EmailField(null=True)
    phonenumber = models.CharField(max_length=15,null=True)
    


# シフト情報
class Shift(models.Model):
    user = models.ForeignKey(Userr, verbose_name='スタッフ', on_delete=models.CASCADE)
    workingtime = models.DateTimeField()
    
    def __str__(self):
        start = timezone.localtime(self.workingtime).strftime('%Y/%m/%d %H:%M')
        return f'{self.user.clerkname}{start}'