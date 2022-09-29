# Generated by Django 3.2 on 2022-09-29 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0017_userr_hourly_wage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userr',
            name='admin_only_text',
            field=models.CharField(default='管理者のみ閲覧可。', max_length=200, null=True, verbose_name='管理者用メモ'),
        ),
        migrations.AlterField(
            model_name='userr',
            name='clerkname',
            field=models.CharField(max_length=20, null=True, unique=True, verbose_name='名前'),
        ),
        migrations.AlterField(
            model_name='userr',
            name='email',
            field=models.EmailField(max_length=255, unique=True, verbose_name='メールアドレス'),
        ),
        migrations.AlterField(
            model_name='userr',
            name='introduction_text',
            field=models.CharField(default='自己紹介文', max_length=200, verbose_name='自己紹介文'),
        ),
    ]
