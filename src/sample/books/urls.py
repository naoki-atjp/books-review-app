from django.urls import path
from django.http import HttpResponse
from . import views

app_name = "books"

urlpatterns = [
    path("ping/", lambda request: HttpResponse("pong"), name="ping"),

    # Category
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path("categories/new/", views.CategoryCreateView.as_view(), name="category_create"),
    path("categories/<int:pk>/edit/", views.CategoryUpdateView.as_view(), name="category_update"),
    path("categories/<int:pk>/delete/", views.CategoryDeleteView.as_view(), name="category_delete"),

    # Google Books Search
    path("search/", views.BookSearchView.as_view(), name="search"),

    # レビューする本を選んだとき：sessionに保存する
    path("select-book/", views.SelectBookView.as_view(), name="select_book"),

    # レビュー作成
    # path("create/", views.ReviewCreateView.as_view(), name="create_review"),

    # レビュー作成を中止（sessionクリア）
    path("cancel/", views.CancelSelectedBookView.as_view(), name="cancel_review"),

    # 特定の書籍のレビュー一覧
    path("detail/<str:book_id>/", views.BookDetailView.as_view(), name="detail"),
    # TODO: 将来的には以下を使う
    # path("<str:book_id>/", views.BookDetailView.as_view(), name="detail"),
]

