#責務：
# 書籍詳細ページで必要なcontextを組み立てる（Viewを薄くする）
# 現在はJSON(dummy)から book/review を取得して整形する
## Viewは build_book_detail_context(book_id) を呼ぶだけにする

from __future__ import annotations
from typing import Any, Dict

# DB接続前はdummy→今後DB取得に差し替え
from core.dummy.reviews_dummy_loader import (
  load_reviews_dummy,
  find_book,
  list_reviews_by_book,
  enrich_review_ui
)


def build_book_detail_context(book_id: str) -> Dict[str, Any]:
  #----------------
  # 書籍詳細のcontextを作る関数
  # view.pyに呼び出される
  # DB接続時に中身差し替え予定
  #----------------

  # json読み込み
  data = load_reviews_dummy()
  book = find_book(data, book_id)

  if not book:
    return {
      "book_not_found": True,
      "book": {"book_id": book_id, "book_title": "書籍が見つかりません"},
      "reviews": [],
    }
  
  # categoryを表示用に変換
  raw_categories = book.get("categories", []) or []
  book["categories"] = [
    c.get("category_name", "")
    for c in raw_categories
    if c.get("category_name")
  ]

  # レビュー一覧取得
  reviews = list_reviews_by_book(data, book_id)

  # UI用整形（評価/いいね/フロー有無の付与）
  reviews = [enrich_review_ui(data, r) for r in reviews]

  # 正常時のcontext
  return {
    "book_not_found": False,
    "book": book,
    "reviews": reviews,
  }