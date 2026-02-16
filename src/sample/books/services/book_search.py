#責務：
# 書籍検索画面用の「検索条件処理 + ページング計算」を行う
# GoogleBooksClientを呼び出し、テンプレ用ViewModelを組み立てて返す
# 最大件数/最大ページなどの上限ルールをここで保証
# Djangoのrequest/responseは扱わない（Viewから呼ばれる純粋関数に寄せる）

import math
from dataclasses import dataclass
from .google_books import GoogleBooksClient, GoogleBooksApiError, BookSearchResult

# Google Books検索の上限設定
MAX_RESULTS_PER_PAGE = 10   # 1ページ10件
MAX_PAGES = 10              # 最大10ページ = 100件
MAX_TOTAL_RESULTS = MAX_RESULTS_PER_PAGE * MAX_PAGES  # 100件

@dataclass(frozen=True)
class BooksSearchViewModel:
  # テンプレに渡すデータ
  query: str
  page: int
  books: list
  total_items: int
  total_pages: int
  page_numbers: list[int]
  has_prev: bool
  has_next: bool

def search_book_for_view(query: str, page: int) -> BooksSearchViewModel:
  #=====================
  # viewsから呼ばれる関数
  # 検索条件およびページ計算処理
  # 失敗時例外を投げる→views側でメッセージ化
  #=====================

  #---------------------
  # ページの安全化
  #---------------------
  safe_page = max(1, min(page, MAX_PAGES))

  per_page = MAX_RESULTS_PER_PAGE
  start_index = (safe_page - 1) * per_page

  #---------------------
  # 上限を超えるのはAPI叩かない
  #---------------------
  if start_index >= MAX_TOTAL_RESULTS:
    total_pages = MAX_PAGES
    return BooksSearchViewModel(
      query=query,
      page=safe_page,
      books=[],
      total_items=MAX_TOTAL_RESULTS,
      total_pages=total_pages,
      page_numbers=list(range(1, total_pages + 1)),
      has_prev=safe_page > 1,
      has_next=False,
    )

  #---------------------
  # API実行
  #---------------------
  client = GoogleBooksClient()
  result: BookSearchResult = client.search(
    query=query,
    start_index=start_index,
    max_results=per_page,
  )

  #---------------------
  # 件数上限を適用→ページ計算
  #---------------------
  total_items_capped = min(result.total_items, MAX_TOTAL_RESULTS)
  total_pages = math.ceil(total_items_capped / per_page) if total_items_capped else 0
  total_pages = min(total_pages, MAX_PAGES)

  return BooksSearchViewModel(
    query=query,
    page=safe_page,
    books=result.books,
    total_items=total_items_capped,
    total_pages=total_pages,
    page_numbers=list(range(1, total_pages + 1)) if total_pages else [],
    has_prev=safe_page > 1,
    has_next=safe_page < total_pages,
  )