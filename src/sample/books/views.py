from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import render
from core.dummy.category_dummy import get_category_context

from .models import Category
from .forms import CategoryForm
from .services.google_books import GoogleBooksApiError

from datetime import timedelta
from django.shortcuts import redirect
from django.views import View
from django.utils import timezone

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from .forms import BookSearchForm
from .services.book_search import search_books_for_view

from core.dummy.reviews_dummy_loader import (
    load_reviews_dummy,
    find_book,
    list_reviews_by_book,
    enrich_review_ui,
)


# =========================
# Category（一覧）
# =========================
class CategoryListView(ListView):
    model = Category
    template_name = "books/category_list.html"
    context_object_name = "categories"
    ordering = ["category_code"]


# =========================
# Category（作成）
# =========================
class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "books/category_form.html"
    success_url = reverse_lazy("books:category_list")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        obj.updated_by = self.request.user
        obj.save()
        return super().form_valid(form)


# =========================
# Category（更新）
# =========================
class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "books/category_form.html"
    success_url = reverse_lazy("books:category_list")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.updated_by = self.request.user
        obj.save()
        return super().form_valid(form)


# =========================
# Category（削除）
# =========================
class CategoryDeleteView(DeleteView):
    model = Category
    template_name = "books/category_confirm_delete.html"
    success_url = reverse_lazy("books:category_list")


# =========================
# Book Search（Google Books）
# =========================
@method_decorator(ensure_csrf_cookie, name="dispatch")
class BookSearchView(View):
    template_name = "books/layout/books_search.html"

    def get(self, request, *args, **kwargs):

        # テンプレに渡す共通値（初期値）
        context = {
            "action_url": reverse("books:search"),
            "error_message":"",
            "query": "",
            "books": [],
            "total_items": 0,
            "total_pages": 0,
            "page": 1,
            "page_numbers": [],
            "has_prev": False,
            "has_next": False,
        }

        # GETパラメータをフォームで受け取って検証する
        form = BookSearchForm(request.GET)
        if not form.is_valid():
            return render(request, self.template_name, context)
    
        query = form.cleaned_data["q"]
        page = form.cleaned_data.get("page") or 1

        context["query"] = query
        context["page"] = page

        # 検索語なし → API叩かない
        if not query:
            return render(request, self.template_name, context)

        try:
            vm = search_books_for_view(query=query, page=page)
        except GoogleBooksApiError as e:
            context["error_message"] = f"検索に失敗しました: {e}"
            return render(request, self.template_name, context)
        
        # 画面用データをまとめて反映
        context.update(
            {
                "books": vm.books,
                "total_items": vm.total_items,
                "total_pages": vm.total_pages,
                "page": vm.page,
                "page_numbers": vm.page_numbers,
                "has_prev": vm.has_prev,
                "has_next": vm.has_next,
            }
        )

        return render(request, self.template_name, context)


# sessionに書籍情報を保存するときのキー
SESSION_SELECTED_BOOK_KEY = "selected_book"
SESSION_SELECTED_BOOK_SAVED_AT_KEY = "selected_book_saved_at"

# セッションに保存する期限：24時間
SELECTED_BOOK_TTL = timedelta(hours=24)


class SelectBookView(View):
    # 検索結果でレビューする書籍をクリックしたときに呼ばれる
    # sessionに書籍情報をメモして /reviews/new/ へ移動

    def post(self, request, *args, **kwargs):
        # POSTで送られてきた本情報を取り出す
        selected_book = {
            "volume_id": request.POST.get("volume_id", ""),
            "book_img": request.POST.get("book_img", ""),
            "book_title": request.POST.get("book_title", ""),
            "author": request.POST.get("author", ""),
            "company": request.POST.get("company", ""),
            "published_date": request.POST.get("published_date", ""),
        }

        if not selected_book["volume_id"] or not selected_book["book_title"]:
            return redirect("books:search")

        # sessionに保存
        request.session[SESSION_SELECTED_BOOK_KEY] = selected_book

        # 保存時刻も格納（期限チェック用）
        request.session[SESSION_SELECTED_BOOK_SAVED_AT_KEY] = timezone.now().isoformat()

        # レビュー作成ページへ遷移
        return redirect("reviews:create")


class CancelSelectedBookView(View):
    # ユーザーがレビュー作成を中止したときに session を削除

    def post(self, request, *args, **kwargs):
        request.session.pop(SESSION_SELECTED_BOOK_KEY, None)
        request.session.pop(SESSION_SELECTED_BOOK_SAVED_AT_KEY, None)
        return redirect("books:search")


class ReviewCreateView(TemplateView):
    # レビュー作成ページ
    # GET: sessionの本情報を表示
    # POST: 投稿時に Review/Book 保存へ
    template_name = "reviews/layout/review_form.html"

    def _get_selected_book_or_none(self):

        selected_book = self.request.session.get(SESSION_SELECTED_BOOK_KEY)
        saved_at_str = self.request.session.get(SESSION_SELECTED_BOOK_SAVED_AT_KEY)

        if not selected_book or not saved_at_str:
            return None

        try:
            saved_at = timezone.datetime.fromisoformat(saved_at_str)

            if timezone.is_naive(saved_at):
                saved_at = timezone.make_aware(saved_at, timezone.get_current_timezone())
        except ValueError:
            return None

        if timezone.now() - saved_at > SELECTED_BOOK_TTL:
            return None

        return selected_book

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        selected_book = self._get_selected_book_or_none()

        # 期限切れ/未選択なら sessionを消して検索へ戻す導線を作成
        if not selected_book:
            # 期限切れのセッションを削除
            self.request.session.pop(SESSION_SELECTED_BOOK_KEY, None)
            self.request.session.pop(SESSION_SELECTED_BOOK_SAVED_AT_KEY, None)

            context["expired"] = True
            context["selected_book"] = None
            return context

        context["expired"] = False
        context["selected_book"] = selected_book

        # デバッグ用 TODO: 最終削除しておく
        # print("----- Google Books Search DEBUG -----")
        # print("query:", query)
        # print("total_items_raw:", total_items_raw)
        # print("total_items_capped:", total_items_capped)
        # print("books_len:", len(books))
        # print("page:", page)
        # print("start_index:", start_index)
        # print("total_pages:", total_pages)
        # print("------------------------------------")

        context.update(get_category_context())
        
        return context
    


class BookDetailView(TemplateView):
    template_name = "books/layout/book_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # URL: /books/detail/<str:book_id>/
        book_id = self.kwargs.get("book_id")

        # JSON読み込み
        data = load_reviews_dummy()

        # book 取得
        book = find_book(data, book_id)

        if not book:
            context["book_not_found"] = True
            context["book"] = {"book_id": book_id, "book_title": "（書籍が見つかりません）"}
            context["reviews"] = []
            return context

        # categories を表示用に変換
        raw_categories = book.get("categories", [])
        book["categories"] = [
            c.get("category_name", "")
            for c in raw_categories
            if c.get("category_name")
        ]

        # レビュー一覧（book_idで絞る）
        reviews = list_reviews_by_book(data, book_id)

        for r in reviews:
            enrich_review_ui(data, r)

        context["book_not_found"] = False
        context["book"] = book
        context["reviews"] = reviews
        return context