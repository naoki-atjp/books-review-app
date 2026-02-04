import json
from django.conf import settings
from django.views.generic import TemplateView
from core.dummy.category_dummy import get_category_context
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from django.shortcuts import render
from core.dummy.reviews_dummy_loader import (
    load_reviews_dummy,
    find_book,
    find_review,
    list_flows_by_review,
    enrich_review_ui,
)


# books側と同じキー
SESSION_SELECTED_BOOK_KEY = "selected_book"
SESSION_SELECTED_BOOK_SAVED_AT_KEY = "selected_book_saved_at"

# セッション期限：books/views.py と合わせる
SELECTED_BOOK_TTL = timedelta(hours=24)


class ReviewCreateView(TemplateView):
    """
    GET : 書籍情報表示
    POST: 完了ページへリダイレクト（今はDB保存なし）
    """
    template_name = "reviews/layout/review_form.html"

    def _get_selected_book_or_none(self):
        # sessionから本情報を取り出す
        selected_book = self.request.session.get(SESSION_SELECTED_BOOK_KEY)
        saved_at_str = self.request.session.get(SESSION_SELECTED_BOOK_SAVED_AT_KEY)

        # 本情報 or 保存時刻が無いなら無効
        if not selected_book or not saved_at_str:
            return None

        # ISO文字列 → datetime へ変換
        try:
            saved_at = timezone.datetime.fromisoformat(saved_at_str)

            # タイムゾーン無しなら付ける
            if timezone.is_naive(saved_at):
                saved_at = timezone.make_aware(saved_at, timezone.get_current_timezone())
        except ValueError:
            return None

        # 期限切れチェック
        if timezone.now() - saved_at > SELECTED_BOOK_TTL:
            return None

        return selected_book

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        selected_book = self._get_selected_book_or_none()

        # 期限切れ / 未選択の場合
        if not selected_book:
            # 期限切れのsessionは削除
            self.request.session.pop(SESSION_SELECTED_BOOK_KEY, None)
            self.request.session.pop(SESSION_SELECTED_BOOK_SAVED_AT_KEY, None)

            context["expired"] = True
            context["selected_book"] = None
            return context

        context["expired"] = False
        context["selected_book"] = selected_book

        # カテゴリダミーデータ
        context.update(get_category_context())

        return context

    def post(self, request, *args, **kwargs):
        # レビュー投稿（今はDB保存なし）
        # 入力OKなら完了ページへ redirect
        selected_book = self._get_selected_book_or_none()

        # 期限切れなら期限切れ表示で返す
        if not selected_book:
            request.session.pop(SESSION_SELECTED_BOOK_KEY, None)
            request.session.pop(SESSION_SELECTED_BOOK_SAVED_AT_KEY, None)

            context = {
                "expired": True,
                "selected_book": None,
            }
            return render(request, self.template_name, context)

        # フォーム値を受け取る
        rating = request.POST.get("rating")

        # チェック（サーバ側）
        if not rating:
            context = self.get_context_data(**kwargs)
            context["error_message"] = "評価が未選択です。"
            return render(request, self.template_name, context)

        # 本来ここでDB保存して review_id を作る
        dummy_review_id = "dummy"

        # 二重投稿防止で本選択sessionを消す
        request.session.pop(SESSION_SELECTED_BOOK_KEY, None)
        request.session.pop(SESSION_SELECTED_BOOK_SAVED_AT_KEY, None)

        # 完了ページへリダイレクト
        complete_url = f"{reverse('reviews:complete')}?review_id={dummy_review_id}"
        return redirect(complete_url)


def review_complete(request):
    # 投稿完了ページ
    review_id = request.GET.get("review_id", "dummy")
    return render(request, "reviews/review_complete.html", {"review_id": review_id})



def review_detail(request, book_id: str, review_id: int):
    # DBなし：JSONから book と review を引いて表示
    # book_id はURLの値
    # review_id は reviews_review.id と照合

    data = load_reviews_dummy()

    book = find_book(data, book_id)
    review = find_review(data, review_id)
    if not book or not review:
        return render(
            request,
            "reviews/layout/review_detail.html",
            {
                "not_found": True,
                "book": {"book_id": book_id, "book_title": "（書籍が見つかりません）"},
                "review": {"review_id": review_id, "review_title": "（レビューが見つかりません）"},
                "flows": [],
            },
        )

    # UI用データ
    enrich_review_ui(data, review)

    # flow 取得（position順）
    flows = list_flows_by_review(data, review_id)

    # カテゴリ表示用
    raw_categories = book.get("categories", [])
    book["categories"] = [
        c.get("category_name", "")
        for c in raw_categories
        if c.get("category_name")
    ]

    return render(
        request,
        "reviews/layout/review_detail.html",
        {
            "not_found": False,
            "book": book,
            "review": review,
            "flows": flows,
        },
    )