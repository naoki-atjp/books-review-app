from django.db import models

# Create your models here.

class Category(models.Model):
  category_code = models.CharField(max_length=30, unique=True, verbose_name='カテゴリーコード')
  category_name = models.CharField(max_length=20, verbose_name='カテゴリ名')

  def __str__(self):
    return self.category_name

class Book(models.Model):
  book_id = models.CharField(max_length=255, unique=True, primary_key=True, verbose_name='書籍ID')
  book_title = models.CharField(max_length=255, verbose_name='書籍名')
  book_img = models.URLField(max_length=500, blank=True, null=True, verbose_name='表紙画像')
  author = models.CharField(max_length=255, blank=True, null=True, verbose_name='著者')
  company = models.CharField(max_length=255, blank=True, null=True, verbose_name='出版社')
  release = models.DateField(null=True, blank=True, verbose_name='発行日')
  categories = models.ManyToManyField(Category, related_name="books")

  def __str__(self):
    return self.book_title