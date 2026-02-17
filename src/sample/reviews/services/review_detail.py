# 責務:
# 「レビュー詳細ページ」で必要な context を作る
# views.py はこの関数を呼ぶだけにする
# DB接続までは JSON(dummy) から取得
# 将来は DB / API に差し替えても views を変えない

from __future__ import annotations
from typing import Any, Dict

from core.dummy.reviews_dummy_loader import (
    load_reviews_dummy,
    find_book,
    find_review_by_book,
    list_flows_by_review,
    enrich_review_ui,
)


def _format_book_categories_for_view(book: dict) -> dict:
  #---------------
  # book["categories"] をテンプレ表示用に整形
  #---------------
  raw_categories = book.get("categories", []) or []

  book["categories"] = [
    c.get("category_name", "")
    for c in raw_categories
    if isinstance(c, dict) and c.get("category_name")
  ]
  return book


def build_review_detail_context(book_id: str, review_id: int) -> Dict[str, Any]:
  #---------------
  # レビュー詳細ページに必要なcontextを返す
  #---------------
  data = load_reviews_dummy()

  book = find_book(data, book_id)
  if not book:
      return {
          "not_found": True,
          "book": {"book_id": book_id, "book_title": "書籍が見つかりません"},
          "review": {"review_id": review_id, "review_title": "レビューが見つかりません"},
          "flows": [],
      }

  # book_id と review_id の両方で一致する review を取る
  review = find_review_by_book(data, book_id, review_id)
  if not review:
      return {
          "not_found": True,
          "book": book,
          "review": {"review_id": review_id, "review_title": "レビューが見つかりません"},
          "flows": [],
      }

  # 表示用整形
  review_vm = enrich_review_ui(data, review)
  flows = list_flows_by_review(data, review_id)
  book = _format_book_categories_for_view(book)

  return {
      "not_found": False,
      "book": book,
      "review": review_vm,
      "flows": flows,
  }