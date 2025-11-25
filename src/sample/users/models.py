from django.db import models

# Create your models here.

class User(models.Model):
  name = models.CharField(max_length=30, verbose_name='ユーザー名')
  email = models.EmailField(max_length=255, unique=True, blank=False, null=False ,verbose_name='メールアドレス')
  password = models.CharField(max_length=128, blank=False, null=False, verbose_name='パスワード')
  icon_img = models.ImageField(upload_to='user_image', blank=True, null=True, verbose_name='ユーザーアイコン')

  def __str__(self):
    return self.name