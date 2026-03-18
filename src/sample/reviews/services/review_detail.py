# 責務:
# 「レビュー詳細ページ」で必要な context を作る
# views.py はこの関数を呼ぶだけにする
from __future__ import annotations
import logging
from typing import Any, Dict, List

# from django.db.models import Count

from books.models import Book
from reviews.models import Review, ReviewGood, Flow

# ロガーの作成・取得
logger = logging.getLogger(__name__)


def _build_star_ui(rating: float) -> Dict[str, Any]:
    #ratingからテンプレ用の星表示データを作る
    # 例: 4.5 → full=4, half=True
    full = int(rating)  # 小数点以下切り捨て
    has_half = (rating - full) >= 0.5

    return {
        "full_stars": range(full),   # テンプレで {% for _ in review.ui.full_stars %} を成立させる
        "has_half_star": has_half,
    }


def _format_book_for_view(book: Book) -> Dict[str, Any]:
    # Bookモデル → テンプレで使いやすい dict に変換
    # book_card_detail_header.html が categories を for で回すので必ず list を入れる
    # categories が ManyToMany の場合は .all() が必要

    categories: List[str] = []

    # Book に categories 属性が無い場合でも落ちないように guard
    if hasattr(book, "categories"):
        try:
            categories = [c.category_name for c in book.categories.all()]

        # TODO: ユーザー目線でも失敗したことがわかるようにする + ログも残す
        except AttributeError as e:
            # NOTE: category_name が無い / categories が想定と違うオブジェクト(想定する例外:仮)
            # logger.exception(f"Book categories format error (AttributeError): {e}")
            logger.exception("Book categories format error (AttributeError): %s", e)
            categories=[]

        except Exception as e:
            # 想定外の例外のための最後の砦 ログを残す
            logger.exception("Unexpected error while building categories: %s", e)
            categories=[]

    return {
        "book_id": getattr(book, "book_id", ""),
        "book_title": getattr(book, "book_title", ""),
        "book_img": getattr(book, "book_img", ""),
        "author": getattr(book, "author", ""),
        "company": getattr(book, "company", ""),
        "release": getattr(book, "release", ""),
        "categories": categories,
    }
    
    # except Exception:
    #     # 本来はここで想定できなかった謎のエラーをログ出力する
    #     # outputlog(file_name, func_name, file_line)
    #     categories = []


def build_review_detail_context(book_id: str, review_id: int) -> Dict[str, Any]:
    # URL: /reviews/books/<book_id>/reviews/<review_id>/
    # book_id は Book.book_id（Google BooksのvolumeId）

    # Review を DB から取得
    # select_related: review.book / review.user を同時に抜いてDB回数を減らす
    review_obj = (
        Review.objects
        .select_related("book", "user")
        .filter(id=review_id)
        .first()
    )

    # レビューが存在しない
    if not review_obj:
        return {
            "not_found": True,
            "book": {"book_id": book_id, "book_title": "書籍が見つかりません"},
            "review": {"review_id": review_id, "review_title": "レビューが見つかりません"},
            "flows": [],
        }

    # URLの book_id と一致するか確認
    if review_obj.book.book_id != book_id:
        return {
            "not_found": True,
            "book": {"book_id": book_id, "book_title": "書籍が見つかりません"},
            "review": {"review_id": review_id, "review_title": "レビューが見つかりません"},
            "flows": [],
        }

    # 学習フローを取得
    flows = list(
        Flow.objects
        .filter(review_id=review_obj.id)
        .order_by("position")
    )

    # いいね数を取得
    likes_count = ReviewGood.objects.filter(review_id=review_obj.id).count()

    # テンプレ用に Review を dict 化（UIデータもここで作る）
    # テンプレは review.ui.user_name / review.ui.full_stars などを参照しているためその形に合わせる
    star_ui = _build_star_ui(float(review_obj.rating))

    review_vm = {
        # テンプレ内で review.id を使ってる（like URL生成）
        "id": review_obj.id,
        "review_id": review_obj.id,
        "review_title": review_obj.review_title,
        "body": review_obj.body,
        "recommended_for": review_obj.recommended_for,
        "rating": float(review_obj.rating),
        "post_date": review_obj.post_date,

        # テンプレが参照するUI用の塊
        "ui": {
            "user_name": getattr(review_obj.user, "name", "no name"),
            "likes_count": likes_count,

            # 星UI
            "full_stars": star_ui["full_stars"],
            "has_half_star": star_ui["has_half_star"],
        },
    }

    # Book もテンプレ用に dict 化
    book_vm = _format_book_for_view(review_obj.book)

    return {
        "not_found": False,
        "book": book_vm,
        "review": review_vm,
        "flows": flows,
    }