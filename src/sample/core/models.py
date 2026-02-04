from django.db import models
from django.conf import settings  # AUTH_USER_MODELを使うため


# 作成日時・更新日時だけを管理する共通クラス
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='作成日時',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        db_index=True,
        verbose_name='更新日時',
    )

    class Meta:
        abstract = True


# 作成者・更新者を管理する共通クラス
class UserAuditModel(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,         # ユーザー削除しても履歴は残す
        null=True,
        blank=True,
        related_name='%(class)s_created',  # 例:review_created, book_created
        verbose_name='作成ユーザー',
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        verbose_name='更新ユーザー',
    )

    class Meta:
        abstract = True


# 論理削除用の共通クラス
class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(
        default=False,
        verbose_name='削除フラグ',
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='削除日時',
    )
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_deleted',
        verbose_name='削除者ユーザー',
    )

    class Meta:
        abstract = True