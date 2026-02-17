from django.db import models
from django.conf import settings
from books.models import Book
from django.utils import timezone
from core.models import TimeStampedModel, UserAuditModel, SoftDeleteModel
from django.db.models import Q 

class Review(TimeStampedModel, UserAuditModel, SoftDeleteModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT,
        verbose_name='作成者',
        related_name='reviews',
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.PROTECT,
        verbose_name='書籍',
        related_name='reviews',
    )
    rating = models.FloatField(
        verbose_name='書籍の評価',
    )
    review_title = models.CharField(
        max_length=30,
        verbose_name='レビュータイトル',
    )
    body = models.TextField(
        max_length=5000,
        verbose_name='レビュー本文',
    )
    recommended_for = models.TextField(
        max_length=200,
        verbose_name='おすすめする人',
    )

    post_date = models.DateField(
        default=timezone.now,
        db_index=True,
        verbose_name='レビュー投稿日',
    )

    def __str__(self):
        return f"{self.book.book_title} - {self.user.name} のレビュー"


class ReviewGood(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True, #未ログイン時のいいねを許容
        blank=True,
        verbose_name='いいねしたユーザー',
        related_name='review_goods',
    )

    # 未ログインユーザーを識別するキー（Cookieに入れる）
    anon_key = models.CharField(
        max_length=64,
        null=True,          # 未ログイン以外は空になるのでNULL許可
        blank=True,
        db_index=True,      # 取り消し検索で使うのでindex
        verbose_name='未ログイン識別キー',
    )

    review = models.ForeignKey(
        "reviews.Review",
        on_delete=models.PROTECT,
        verbose_name='レビュー',
        related_name='goods',
    )

    def __str__(self):
        # user がある時は user名、ない時は未ログイン扱い
        who = self.user.name if self.user else f"未ログイン({self.anon_key})"
        return f"{who} が「{self.review.review_title}」に付けたいいね"

    class Meta:
        verbose_name = 'レビューいいね'
        verbose_name_plural = 'レビューいいね'

        # 条件付きとして constraints を使う
        constraints = [
            # ログインいいね：user が入ってる時だけ (review, user) を一意にする
            models.UniqueConstraint(
                fields=["review", "user"],
                condition=Q(user__isnull=False),
                name="uniq_reviewgood_by_user",
            ),

            # 未ログインいいね：anon_key が入ってる時だけ (review, anon_key) を一意にする
            models.UniqueConstraint(
                fields=["review", "anon_key"],
                condition=Q(anon_key__isnull=False),
                name="uniq_reviewgood_by_anon",
            ),

            # user も anon_key も両方NULLは禁止（どっちか必須）
            models.CheckConstraint(
                check=Q(user__isnull=False) | Q(anon_key__isnull=False),
                name="check_reviewgood_user_or_anon_required",
            ),
        ]

class Flow(TimeStampedModel, UserAuditModel, SoftDeleteModel):
    review = models.ForeignKey(
        Review,
        on_delete=models.PROTECT,
        verbose_name='レビュー',
        related_name='flows',
    )
    position = models.PositiveSmallIntegerField(
        blank=False,
        null=False,
        verbose_name='学習フローSTEP',
    )
    flow_title = models.CharField(
        max_length=50,
        blank=False,
        null=False,
        verbose_name='STEP名',
    )
    flow_content = models.TextField(
        max_length=300,
        blank=False,
        null=False,
        verbose_name='STEP内容',
    )
    duration_text = models.CharField(
        max_length=20,
        blank=False,
        null=False,
        verbose_name='所要時間',
    )

    def __str__(self):
        return f"{self.review.review_title} のレビューで作成された学習フロー（STEP {self.position}）"

    class Meta:
        verbose_name = '学習フロー'
        verbose_name_plural = '学習フロー'
        ordering = ['review', 'position']  # デフォルトでSTEP順に並ぶように
