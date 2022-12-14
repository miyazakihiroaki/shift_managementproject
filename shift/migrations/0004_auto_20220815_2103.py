# Generated by Django 3.2 on 2022-08-15 12:03

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shift', '0003_shift'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shop_info',
            name='finish_workingtime',
            field=models.TimeField(blank=True, default=datetime.time(21, 0), verbose_name='閉店時刻'),
        ),
        migrations.AlterField(
            model_name='shop_info',
            name='start_workingtime',
            field=models.TimeField(blank=True, default=datetime.time(9, 0), verbose_name='始業時刻'),
        ),
    ]
