# 責務：
# いいねのトグル処理をサービスに寄せる

from __future__ import annotations
from typing import Any, Dict

from django.contrib.auth.models import AbstractBaseUser
from django.db.models import QuerySet

from reviews.models import Review, ReviewGood


def toggle_like_dummy(session: Any, review_id: int) -> Dict[str, Any]:
    # ダミーいいねトグル
    # セッションをDB代わりに使う
    # 404を消して、UIの挙動だけ確認する用

    liked_key = f"liked_review_{review_id}"
    count_key = f"liked_review_count_{review_id}"
    is_liked = bool(session.get(liked_key, False))

    try:
        current_count = int(session.get(count_key, 0))
    except (TypeError, ValueError):
        current_count = 0

    new_is_liked = not is_liked

    if new_is_liked:
        new_count = current_count + 1
    else:
        new_count = max(current_count - 1, 0)

    session[liked_key] = new_is_liked
    session[count_key] = new_count

    return {
        "ok": True,
        "review_id": review_id,
        "liked": new_is_liked,
        "likes_count": new_count,
    }


def toggle_like_db(user: AbstractBaseUser, book_id: str, review_id: int) -> Dict[str, Any]:
    # DBいいねトグル（将来用）
    # URL差し替えで有効化する
    # review_idのレビューが存在し、URLのbook_idと一致するか確認

    # レビューを取得
    review = Review.objects.select_related("book").filter(id=review_id).first()

    # 存在しない / book_idが一致しない → 404扱い
    if not review or review.book.book_id != book_id:
        return {
            "ok": False,
            "status": 404,
            "message": "review not found",
        }

    # 既にいいね済みか確認
    existing = ReviewGood.objects.filter(user=user, review=review).first()

    # トグル（あれば削除、なければ作成）
    if existing:
        existing.delete()
        liked = False
    else:
        ReviewGood.objects.create(user=user, review=review)
        liked = True

    # 最新のいいね数を数える
    likes_count = ReviewGood.objects.filter(review=review).count()

    return {
        "ok": True,
        "liked": liked,
        "likes_count": likes_count,
    }