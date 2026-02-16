from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import render

from .models import Category
from .forms import CategoryForm
from .services.google_books import GoogleBooksApiError

from django.shortcuts import redirect
from django.views import View

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from .forms import BookSearchForm
from .services.book_search import search_books_for_view

from books.services.selected_book_session import (
    build_selected_book_from_post,
    is_valid_selected_book,
    save_selected_book_to_session,
    pop_selected_book_from_session,
)

from books.services.books_detail import build_book_detail_context


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


class SelectBookView(View):
    # 検索結果でレビューする書籍をクリックしたときに呼ばれる
    # sessionに書籍情報をメモして /reviews/new/ へ移動

    def post(self, request, *args, **kwargs):
        # POSTデータから「選択した本」を作る
        book = build_selected_book_from_post(request.POST)

        # 必須情報が足りないなら検索に戻す
        if not is_valid_selected_book(book):
            return redirect("books:search")

        # セッションへ保存
        save_selected_book_to_session(request.session, book)

        # レビュー作成ページへ
        return redirect("reviews:create")


class CancelSelectedBookView(View):
    # ユーザーがレビュー作成を中止したときに session を削除

    def post(self, request, *args, **kwargs):
        pop_selected_book_from_session(request.session)
        return redirect("books:search")


class BookDetailView(TemplateView):
    template_name = "books/layout/book_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # URL: /books/detail/<str:book_id>/
        book_id = self.kwargs.get("book_id")

        context.update(build_book_detail_context(book_id))

        return context