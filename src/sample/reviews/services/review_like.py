# 責務：
# いいねのトグル処理をサービスに寄せる

from __future__ import annotations
from typing import Any, Dict, Optional

from django.contrib.auth.models import AbstractBaseUser
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


def toggle_like_db(
    user: Optional[AbstractBaseUser],
    anon_key: Optional[str],
    book_id: str,
    review_id: int
) -> Dict[str, Any]:
    #DBいいねトグル（ログイン/未ログイン両対応）
    # ログイン: (review, user) で一意
    # 未ログイン: (review, anon_key) で一意

    #DB制約:
    # review+user は userがNULLじゃない時だけユニーク
    # review+anon_key は anon_keyがNULLじゃない時だけユニーク

    # 引数チェック（どっちも無いのはNG）
    if user is None and not anon_key:
        return {
            "ok": False,
            "status": 400,
            "message": "user or anon_key is required",
        }

    # レビュー存在チェック + book_id一致チェック
    review = Review.objects.select_related("book").filter(id=review_id).first()

    if not review or review.book.book_id != book_id:
        return {
            "ok": False,
            "status": 404,
            "message": "review not found",
        }

    # 既にいいね済みかチェック（user or anon_key で分岐）
    if user is not None:
        existing = ReviewGood.objects.filter(review=review, user=user).first()
    else:
        existing = ReviewGood.objects.filter(review=review, anon_key=anon_key).first()

    # トグル（あれば削除、なければ作成）
    if existing:
        existing.delete()
        liked = False
    else:
        # user または anon_key の片方だけを入れて作る
        ReviewGood.objects.create(
            review=review,
            user=user if user is not None else None,
            anon_key=anon_key if user is None else None,
        )
        liked = True

    # 最新いいね数
    likes_count = ReviewGood.objects.filter(review=review).count()

    return {
        "ok": True,
        "liked": liked,
        "likes_count": likes_count,
    }