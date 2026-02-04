import math
import json
from django.conf import settings
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.middleware.csrf import get_token
from django.shortcuts import render
# from django.contrib.auth.mixins import LoginRequiredMixin
from core.dummy.category_dummy import get_category_context

from .models import Category
from .forms import CategoryForm
from .services.google_books import GoogleBooksClient, GoogleBooksApiError

from datetime import timedelta
from django.shortcuts import redirect
from django.views import View
from django.utils import timezone

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

from core.dummy.reviews_dummy_loader import (
    load_reviews_dummy,
    find_book,
    list_reviews_by_book,
    enrich_review_ui,
)


# Google Books検索の上限設定
MAX_RESULTS_PER_PAGE = 10   # 1ページ10件
MAX_PAGES = 10              # 最大10ページ = 100件
MAX_TOTAL_RESULTS = MAX_RESULTS_PER_PAGE * MAX_PAGES  # 100件


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
        get_token(request)

        context = {}

        # 検索フォームのaction（/books/search/）
        context["action_url"] = reverse("books:search")

        # GETパラメータ
        query = request.GET.get("q", "").strip()
        context["query"] = query

        # 初期値
        context["books"] = []
        context["total_items"] = 0
        context["total_pages"] = 0
        context["page"] = 1
        context["page_numbers"] = []
        context["has_prev"] = False
        context["has_next"] = False
        context["error_message"] = ""

        # 検索語なし → API叩かない
        if not query:
            return render(request, self.template_name, context)

        # page
        page_str = request.GET.get("page", "1")
        try:
            page = int(page_str)
        except ValueError:
            page = 1

        page = max(page, 1)
        page = min(page, MAX_PAGES)
        context["page"] = page

        per_page = MAX_RESULTS_PER_PAGE
        start_index = (page - 1) * per_page

        if start_index >= MAX_TOTAL_RESULTS:
            context["total_items"] = MAX_TOTAL_RESULTS
            context["total_pages"] = MAX_PAGES
            context["page_numbers"] = list(range(1, MAX_PAGES + 1))
            context["has_prev"] = page > 1
            context["has_next"] = False
            return render(request, self.template_name, context)

        client = GoogleBooksClient()

        try:
            result = client.search(query=query, start_index=start_index, max_results=per_page)
        except GoogleBooksApiError as e:
            context["error_message"] = f"検索に失敗しました: {e}"
            return render(request, self.template_name, context)

        books = result.books
        total_items_raw = result.total_items

        total_items_capped = min(total_items_raw, MAX_TOTAL_RESULTS)

        total_pages = math.ceil(total_items_capped / per_page) if total_items_capped else 0
        total_pages = min(total_pages, MAX_PAGES)

        context["books"] = books
        context["total_items"] = total_items_capped
        context["total_pages"] = total_pages
        context["page_numbers"] = list(range(1, total_pages + 1))
        context["has_prev"] = page > 1
        context["has_next"] = (page < total_pages)

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