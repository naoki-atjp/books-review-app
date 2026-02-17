#責務：
# 書籍詳細ページで必要なcontextを組み立てる（Viewを薄くする）
## Viewは build_book_detail_context(book_id) を呼ぶだけにする

from __future__ import annotations
from typing import Any, Dict, List
from django.db.models import Count

from books.models import Book
from reviews.models import Review

def _build_review_ui(review: Review) -> Dict[str, Any]:
    # 画面表示用に整形
    # review.ui.user_name
    # review.ui.likes_count
    # review.ui.full_stars / review.ui.has_half_star
    # review.ui.has_flow

    # likes_count
    # ReviewGood の related_name='goods' を使って数える
    likes_count = review.goods.count()

    # user_name（表示名）
    user_name = getattr(review.user, "name", "") or review.user.username

    # rating からUI用に計算
    rating = float(review.rating or 0)

    # 例：4.5 → full_stars=4, has_half_star=True
    full_stars = int(rating)  # 小数点切り捨て
    has_half_star = (rating - full_stars) >= 0.5

    # 学習フロー有無
    # Flow の related_name='flows' を使う
    has_flow = review.flows.exists()

    return {
        "user_name": user_name,
        "likes_count": likes_count,
        "full_stars": range(full_stars),  # テンプレの for で回す用
        "has_half_star": has_half_star,
        "has_flow": has_flow,
    }


def build_book_detail_context(book_id: str) -> Dict[str, Any]:
  #----------------
  # 書籍詳細のcontextを作る関数
  # view.pyに呼び出される
  # その Book に紐づく Review を一覧で返す
  #----------------

    # 書籍を DB から取得
    # SoftDeleteを使っているので is_deleted=False を条件に入れる
    book = Book.objects.filter(book_id=book_id, is_deleted=False).first()

    # 見つからなければ not_found の context を返す
    if not book:
        return {
            "book_not_found": True,
            "book": {"book_id": book_id, "book_title": "書籍が見つかりません"},
            "reviews": [],
        }

    # レビュー一覧を DB から取得
    # select_related("user") で user を一緒に取得（N+1防止）
    # prefetch_related("goods", "flows") で関連も先読み（N+1防止）
    reviews_qs = (
        Review.objects.filter(book=book, is_deleted=False)
        .select_related("user")
        .prefetch_related("goods", "flows")
        .order_by("-post_date", "-id")
    )

    # UI用の情報を付けてテンプレに渡す
    reviews: List[Review] = list(reviews_qs)

    for r in reviews:
        # テンプレで review.ui.xxx を参照しているので ui を付与する
        r.ui = _build_review_ui(r)  # type: ignore[attr-defined]

    return {
        "book_not_found": False,
        "book": book,
        "reviews": reviews,
    }