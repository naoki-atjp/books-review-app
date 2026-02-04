from django.templatetags.static import static
from core.dummy.reviews_dummy_loader import (
    load_reviews_dummy,
    enrich_review_ui,
    find_book,
)

# 既存関数を再利用
from core.dummy.reviews_dummy_loader import (
    load_reviews_dummy,
    enrich_review_ui,
    find_book,
)


def _resolve_book_image_url(book: dict | None) -> str:
    # books.book_img から表示用URLを作る
    # ルール（DB想定に寄せる）:
    # - book_img が空なら dummy_book.svg を使う
    # - book_img が "img/xxx.svg" のような static 相対パスなら static() でURL化する
    if not book:
        return static("img/dummy_book.svg")

    book_img = book.get("book_img", "")

    # 空ならフォールバック
    if not isinstance(book_img, str) or book_img.strip() == "":
        return static("img/dummy_book.svg")

    return static(book_img)


def list_my_reviews_for_mypage(user_id: int) -> list[dict]:
    # マイページ表示用：自分のレビュー一覧を返す
    # - reviews_review を user_id で絞り込み
    # - enrich_review_ui でテンプレ用の ui 情報を補完
    # - book_id -> books を引いて書籍画像URLを付ける
    data = load_reviews_dummy()

    # 自分のレビューだけに絞る
    all_reviews = data.get("reviews_review", [])
    my_reviews = [
        r for r in all_reviews
        if int(r.get("user_id", 0)) == int(user_id)
    ]

    # UI向け加工 + book画像追加
    result: list[dict] = []
    for r in my_reviews:
        r = enrich_review_ui(data, r)

        # book を引く（DBのJOINの代わり）
        book = find_book(data, r.get("book_id"))
        r["book"] = book

        r["book_image_url"] = _resolve_book_image_url(book)

        result.append(r)

    return result