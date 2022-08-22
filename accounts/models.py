from distutils.command.upload import upload
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class UserManager(BaseUserManager):

    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

# カスタムユーザーモデル
class Userr(AbstractBaseUser):
    
    clerkname = models.CharField(
        max_length=20,
        unique=True,
        null=True,
    )
    
    email = models.EmailField(
        max_length=255,
        # emailの重複を防ぐ
        unique=True,
    )
    
    personalimage = models.ImageField(upload_to='media',verbose_name='プロフィール画像',null = True, blank = True)

    introduction_text = models.CharField(max_length=200, default = '自己紹介文')
    
    #管理者のみ閲覧、編集可
    admin_only_text = models.CharField(max_length=200,default = '管理者のみ閲覧可。', null=True,)
    
    #0:一般店員、1:店長
    category = models.IntegerField('ユーザー種別', default=0)
    
    is_active = models.BooleanField(default=True)

    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    # USERNAME_FIELD = 'clerkname'こうするとメールアドレスで認証できない
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'

    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
    
    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
    
    class Meta:
        verbose_name = ('user')
        # verbose_name_plural = ('users')


# def __str__(self)により、管理画面に表示されるモデル内のデータ（レコード）を判別するための、名前（文字列）を定義する
    
    