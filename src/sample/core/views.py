from django.views.generic import TemplateView
from .dummy.review_dummy import get_recent_reviews
from books.services.categories import get_categories_for_view

class HomeView(TemplateView):
    template_name = "home.html"

    # カテゴリ仮データ
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recent_reviews"] = get_recent_reviews(limit=6)

        # 書籍データ一覧 (仮)
        context["books"] = [
            {
                "book_title": "Flutter実践開発",
                "author": "渡部陽太",
                "book_img": "",
                "avg_rating": 4.8,
                "review_count": 32,
                "categories": ["モバイル開発", "フロントエンド", "テスト"],
            },
            {
                "book_title": "もう1冊の本",
                "author": "著者A",
                "book_img": "",
                "avg_rating": 4.2,
                "review_count": 10,
                "categories": ["バックエンド"],
            },
            {
                "book_title": "もう1冊の本",
                "author": "著者A",
                "book_img": "",
                "avg_rating": 4.2,
                "review_count": 10,
                "categories": ["バックエンド"],
            },
            {
                "book_title": "もう1冊の本",
                "author": "著者A",
                "book_img": "",
                "avg_rating": 4.2,
                "review_count": 10,
                "categories": ["バックエンド"],
            },
            {
                "book_title": "もう1冊の本",
                "author": "著者A",
                "book_img": "",
                "avg_rating": 4.2,
                "review_count": 10,
                "categories": ["バックエンド"],
            },
            {
                "book_title": "もう1冊の本",
                "author": "著者A",
                "book_img": "",
                "avg_rating": 4.2,
                "review_count": 10,
                "categories": ["バックエンド"],
            },
        ]

        context.update(get_categories_for_view())

        return context
