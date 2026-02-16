#責務：
# Google Books APIを叩く「クライアント」を提供する
# 外部APIのレスポンスを、アプリ内の扱いやすい型（BookItem等）へ変換する
# 外部API由来の例外は GoogleBooksApiError に統一して上位へ投げる
# ページ計算や画面都合の加工は book_search.py 側で行う

import requests
from dataclasses import dataclass
from typing import Any

GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"
GOOGLE_BOOKS_TIMEOUT = 10


# =========================
# 書籍検索APIのデータ構造
# =========================

@dataclass(frozen=True)
class BookItem:
    volume_id: str
    book_img: str
    book_title: str
    author: str
    company: str
    published_date: str


@dataclass(frozen=True)
class BookSearchResult:
    total_items: int
    books: list[BookItem]


# =========================
# 例外を統一
# =========================
class GoogleBooksApiError(Exception):
    pass

# =========================
# Google Books API クライアント
# =========================
class GoogleBooksClient:

    def __init__(self, session: requests.Session | None = None) -> None:
        self._session = session or requests.Session()

    def search(self, query: str, start_index: int = 0, max_results: int = 10) -> BookSearchResult:
        # 書籍検索
        # query: 検索ワード
        # start_index: ページング用（何件目から）
        # max_results: 1ページの件数
        params = {
            "q": query,
            "startIndex": start_index,
            "maxResults": max_results,
            "printType": "books",
        }

        try:
            res = self._session.get(
                GOOGLE_BOOKS_API_URL,
                params=params,
                timeout=GOOGLE_BOOKS_TIMEOUT,
            )
            res.raise_for_status()
        except requests.RequestException as e:
            raise GoogleBooksApiError(str(e)) from e

        data = res.json() or {}

        total_items = int(data.get("totalItems", 0) or 0)
        items = data.get("items", []) or []

        books = [self._convert_item_to_book(item) for item in items]

        return BookSearchResult(total_items=total_items, books=books)

    # =======================
    # データの変換・整形
    # =======================
    def _convert_item_to_book(self, item: dict[str, Any]) -> BookItem:
        volume_id = str(item.get("id", "") or "")

        # 1件分(item)を、テンプレ表示用のBookItemに変換
        volume = item.get("volumeInfo", {}) or {}

        image_links = volume.get("imageLinks", {}) or {}
        thumbnail = image_links.get("thumbnail", "") or ""

        title = volume.get("title", "") or ""

        authors_raw = volume.get("authors")
        author = self._pick_first_author(authors_raw)

        publisher_raw = volume.get("publisher")
        company = self._pick_first_publisher(publisher_raw)

        published_date_raw = volume.get("publishedDate", "") or ""
        published_date = self._format_published_date_jp(published_date_raw)

        return BookItem(
            volume_id=volume_id,
            book_img=thumbnail,
            book_title=title,
            author=author,
            company=company,
            published_date=published_date,
        )

    def _pick_first_author(self, authors_raw: Any) -> str:
        # authorsが複数なら先頭だけ表示
        if isinstance(authors_raw, list):
            return str(authors_raw[0]).strip() if authors_raw else ""
        if isinstance(authors_raw, str):
            return authors_raw.strip()
        return ""

    def _pick_first_publisher(self, publisher_raw: Any) -> str:
        if not publisher_raw:
            return ""

        if isinstance(publisher_raw, list):
            publisher_raw = publisher_raw[0] if publisher_raw else ""

        if not isinstance(publisher_raw, str):
            return ""

        text = publisher_raw.strip()

        separators = [" / ", "/", "・", ",", "，", ";", "；"]
        for sep in separators:
            if sep in text:
                return text.split(sep)[0].strip()

        return text

    def _format_published_date_jp(self, published_date_raw: str) -> str:
        # "2023" / "2023-05" / "2023-05-10" を "2023年" / "2023年5月に変換"
        if not published_date_raw:
            return ""

        parts = published_date_raw.split("-")

        year = parts[0] if len(parts) >= 1 else ""
        if not year.isdigit():
            # 変な形式が来たときはそのまま返す
            return published_date_raw

        # 月があれば "YYYY年M月"、なければ "YYYY年"
        if len(parts) >= 2 and parts[1].isdigit():
            month = str(int(parts[1]))
            return f"{year}年{month}月"

        return f"{year}年"