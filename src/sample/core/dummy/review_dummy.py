from copy import deepcopy

# レビュー本文を抜粋する関数
def make_preview(body: str, length: int = 90) -> str:

    if len(body) <= length:
        return body

    return body[:length] + "..."

def build_review(
    *,
    user_name: str,
    user_icon_url: str,
    posted_at: str,
    book_title: str,
    book_cover_url: str,
    rating: float,
    review_title: str,
    body: str,
    good_count: int = 0,
    has_flow: bool = False,
    book_detail_url: str = "#",
    review_detail_url: str = "#",
) -> dict:

    return {
        "user": {
            "name": user_name,
            "icon_url": user_icon_url,
        },
        "posted_at": posted_at,
        "book": {
            "title": book_title,
            "cover_url": book_cover_url,
            "detail_url": book_detail_url,
        },
        "rating": rating,
        "title": review_title,
        "body_preview": make_preview(body),
        "good_count": good_count,
        "has_flow": has_flow,
        "detail_url": review_detail_url,
    }

DUMMY_REVIEWS = [
    build_review(
        user_name="佐藤太郎",
        user_icon_url="/static/img/dummy/user_1.png",
        posted_at="2025-10-25",
        book_title="Flutter実践開発",
        book_cover_url="/static/img/dummy/book_flutter.png",
        rating=4.5,
        review_title="基礎を学習した後の“実践的な”基礎学習におすすめ！",
        body=(
            "Flutter入門の基礎本を学習した後にこの本を学習しました。"
            "基礎的な内容ではありながら、実践的な視点でDart言語の書き方や"
            "Widgetの使い方が説明されていて、実務視点で学べる構成が良かったです。"
            "特に状態管理やUI設計の章が役立ちました。"
        ),
        good_count=52,
        has_flow=False,
        book_detail_url="/books/1/",
        review_detail_url="/reviews/1/",
    ),

    build_review(
        user_name="鈴木花子",
        user_icon_url="/static/img/dummy/user_2.png",
        posted_at="2025-10-20",
        book_title="TypeScript実践ガイド",
        book_cover_url="/static/img/dummy/book_ts.png",
        rating=5.0,
        review_title="型の考え方が一気に整理された",
        body=(
            "型の基本から実務で困りやすい設計まで段階的に説明されていて、"
            "読み終わったあとにコードの読みやすさが確実に上がりました。"
            "ジェネリクスやユーティリティ型の章が特に良かったです。"
        ),
        good_count=88,
        has_flow=True,
        book_detail_url="/books/2/",
        review_detail_url="/reviews/2/",
    ),

    build_review(
        user_name="田中健",
        user_icon_url="/static/img/dummy/user_3.png",
        posted_at="2025-10-05",
        book_title="Clean Architecture 入門",
        book_cover_url="/static/img/dummy/book_ca.png",
        rating=4.0,
        review_title="設計の視点が身につく",
        body=(
            "小さなアプリのうちから設計を意識する大切さが学べました。"
            "図が多く、抽象的な概念もイメージしやすい構成です。"
            "ただし、完全な初心者には少し難しい部分もあるかもしれません。"
        ),
        good_count=27,
        has_flow=True,
        book_detail_url="/books/3/",
        review_detail_url="/reviews/3/",
    ),

    build_review(
        user_name="伊藤誠",
        user_icon_url="/static/img/dummy/user_4.png",
        posted_at="2025-09-28",
        book_title="Pythonデータ分析の基礎",
        book_cover_url="/static/img/dummy/book_py.png",
        rating=3.5,
        review_title="ハンズオン形式で手を動かせる",
        body=(
            "numpyやpandasの基本操作を、短い課題とセットで学べるのが良いです。"
            "例題のデータセットも現実的で、学習のモチベーションが保てました。"
        ),
        good_count=19,
        has_flow=False,
        book_detail_url="/books/4/",
        review_detail_url="/reviews/4/",
    ),

    build_review(
        user_name="山本彩",
        user_icon_url="/static/img/dummy/user_5.png",
        posted_at="2025-09-10",
        book_title="Reactパフォーマンス最適化",
        book_cover_url="/static/img/dummy/book_react_perf.png",
        rating=4.5,
        review_title="実務で効く改善パターンが多い",
        body=(
            "レンダリング最適化やメモ化の基本から、"
            "計測・ボトルネック特定の流れまでまとまっていました。"
            "小さな改善が積み重なる感覚を掴める本です。"
        ),
        good_count=44,
        has_flow=True,
        book_detail_url="/books/5/",
        review_detail_url="/reviews/5/",
    ),

    build_review(
        user_name="中村優",
        user_icon_url="/static/img/dummy/user_6.png",
        posted_at="2025-08-30",
        book_title="テスト駆動開発 実践",
        book_cover_url="/static/img/dummy/book_tdd.png",
        rating=4.0,
        review_title="テストを書く怖さが減った",
        body=(
            "最初は抽象的に感じましたが、"
            "小さな例を積み上げて理解できる構成なので後半で一気に繋がりました。"
            "レビュー対象のプロジェクトにもすぐ試したくなります。"
        ),
        good_count=31,
        has_flow=False,
        book_detail_url="/books/6/",
        review_detail_url="/reviews/6/",
    ),
]


# トップ用
def get_recent_reviews(limit: int = 6) -> list:

    # 元データを壊さないためにコピー
    reviews = deepcopy(DUMMY_REVIEWS)
    reviews.sort(key=lambda r: r.get("posted_at", ""), reverse=True)

    return reviews[:limit]


def get_popular_reviews(limit: int = 6) -> list:

    reviews = deepcopy(DUMMY_REVIEWS)
    reviews.sort(key=lambda r: r.get("good_count", 0), reverse=True)

    return reviews[:limit]