from django.db import models
from users.models import User
from books.models import Book

# Create your models here.

class Review(models.Model):
  user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='作成者', related_name='reviews')
  book = models.ForeignKey(Book, on_delete=models.PROTECT, verbose_name='書籍', related_name='reviews')
  rating = models.FloatField(blank=False, null=False, verbose_name='書籍の評価')
  review_title =models.CharField(max_length=30, blank=False, null=False, verbose_name='レビュータイトル')
  body = models.TextField(max_length=5000, blank=False, null=False, verbose_name='レビュー本文')
  recommended_for = models.TextField(max_length=200, blank=False, null=False, verbose_name='おすすめする人')
  post_date = models.DateField(auto_now_add=True, verbose_name='投稿日')
  created_at = models.DateTimeField(auto_now_add=True, verbose_name='投稿日時')

  def __str__(self):
    return f"{self.book.book_title} - {self.user.name} のレビュー"

class Review_Good(models.Model):
  user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='ユーザー')
  review = models.ForeignKey(Review, on_delete=models.PROTECT, verbose_name='レビュー')

  def __str__(self):
    return f"{self.user.name} さんのレビューに付いたいいね"
  
  class Meta:
    unique_together = ('user', 'review')
  
class Flow(models.Model):
  review = models.ForeignKey(Review, on_delete=models.PROTECT, verbose_name='レビュー')
  position = models.PositiveSmallIntegerField(blank=False, null=False, verbose_name='学習フローSTEP')
  flow_title = models.CharField(max_length=50, blank=False, null=False, verbose_name='STEP名')
  flow_content = models.TextField(max_length=300, blank=False, null=False, verbose_name='STEP内容')
  duration_text = models.CharField(max_length=20, blank=False, null=False, verbose_name='所要時間')

  def __str__(self):
    return f"{self.review.review_title} のレビューで作成された学習フロー"