# Generated by Django 3.2 on 2022-09-23 04:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0016_alter_userr_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='userr',
            name='hourly_wage',
            field=models.IntegerField(default=1000, verbose_name='時給'),
        ),
    ]
