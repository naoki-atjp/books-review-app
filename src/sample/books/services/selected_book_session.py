#責務：
# 「検索結果で選んだ本」をセッションに保存/取得/削除する処理を集約する
# セッション期限（TTL）を一元管理し、期限切れ判定もここで行う
# View側はこのモジュールの関数を呼ぶだけにして、session構造を直接触らない

from __future__ import annotations
from dataclasses import dataclass
from datetime import timedelta
from typing import Any
from django.utils import timezone


# sessionに書籍情報を保存するときのキー
SESSION_SELECTED_BOOK_KEY = "selected_book"
SESSION_SELECTED_BOOK_SAVED_AT_KEY = "selected_book_saved_at"

# セッションに保存する期限：24時間
SELECTED_BOOK_TTL = timedelta(hours=24)


@dataclass(frozen=True)
class SelectedBook:
  #---------------------
  # セッションに入れておきたい選択肢た本の型
  #---------------------
  volume_id: str
  book_img: str
  book_title: str
  author: str
  company: str
  published_date: str

def build_selected_book_from_post(post_data: Any) -> SelectedBook:
  #---------------------
  # POSTデータからSelectedBookを作る
  #---------------------
  return SelectedBook(
    volume_id=(post_data.get("volume_id") or ""),
    book_img=(post_data.get("book_img") or ""),
    book_title=(post_data.get("book_title") or ""),
    author=(post_data.get("author") or ""),
    company=(post_data.get("company") or ""),
    published_date=(post_data.get("published_date") or ""),
  )

def is_valid_selected_book(book: SelectedBook) -> bool:
  #---------------------
  # 必須項目チェック
  #---------------------
  return bool(book.volume_id and book.book_title)

def save_selected_book_to_session(session: Any, book: SelectedBook) -> None:
  #---------------------
  # セッションへ保存
  #---------------------
  session[SESSION_SELECTED_BOOK_KEY] = {
    "volume_id": book.volume_id,
    "book_img": book.book_img,
    "book_title": book.book_title,
    "author": book.author,
    "company": book.company,
    "published_date": book.published_date,
  }
  session[SESSION_SELECTED_BOOK_SAVED_AT_KEY] = timezone.now().isoformat()

def pop_selected_book_from_session(session: Any) -> None:
  #---------------------
  # セッションから削除
  #---------------------
  session.pop(SESSION_SELECTED_BOOK_KEY, None)
  session.pop(SESSION_SELECTED_BOOK_SAVED_AT_KEY, None)

def get_selected_book_or_none(session: Any) -> SelectedBook | None:
  #---------------------
  # セッションから取得
  #---------------------
  selected_book = session.get(SESSION_SELECTED_BOOK_KEY)
  saved_at_str = session.get(SESSION_SELECTED_BOOK_SAVED_AT_KEY)

  if not selected_book or not saved_at_str:
    return None
  
  # --- 保存時刻のパース ---
  try:
    saved_at = timezone.datetime.fromisoformat(saved_at_str)
    if timezone.is_naive(saved_at):
      saved_at = timezone.make_aware(saved_at, timezone.get_current_timezone())
  except ValueError:
    return None
  
  # --- 期限切れ判定 ---
  if timezone.now() - saved_at > SELECTED_BOOK_TTL:
    return None
  
  # --- SelectedBookに変換 ---
  return SelectedBook(
    volume_id=(selected_book.get("volume_id") or ""),
    book_img=(selected_book.get("book_img") or ""),
    book_title=(selected_book.get("book_title") or ""),
    author=(selected_book.get("author") or ""),
    company=(selected_book.get("company") or ""),
    published_date=(selected_book.get("published_date") or ""),
  )
