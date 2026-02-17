from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.urls import reverse
import secrets

from books.services.selected_book_session import (
    get_selected_book_or_none,
    pop_selected_book_from_session,
)
from books.services.categories import get_categories_for_view
from reviews.services.review_detail import build_review_detail_context
from .forms import ReviewCreateForm
from reviews.services.review_like import toggle_like_db


class ReviewCreateView(TemplateView):
    #-----------------
    #GET : 書籍情報表示
    #POST: 完了ページへリダイレクト（今はDB保存なし）
    #-----------------
    template_name = "reviews/layout/review_form.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # カテゴリダミーデータ
        context.update(get_categories_for_view())
        selected_book = get_selected_book_or_none(self.request.session)

        # 期限切れ / 未選択の場合
        if not selected_book:
            pop_selected_book_from_session(self.request.session)
            context["expired"] = True
            context["selected_book"] = None
            return context
        
        context["expired"] = False
        context["selected_book"] = selected_book
        context["form"] = ReviewCreateForm(category_choices=[])
        context["posted_categories"] = []
        context["posted_rating"] = ""

        return context


    def post(self, request, *args, **kwargs):
        # まずは選択中の書籍を確認
        selected_book = get_selected_book_or_none(request.session)

        # 期限切れなら期限切れ表示で返す
        if not selected_book:
            pop_selected_book_from_session(request.session)
            context = {
                "expired": True,
                "selected_book": None,
            }
            return render(request, self.template_name, context)

        # categories の choices を作る
        categories_context = get_categories_for_view()
        language_categories = categories_context.get("language_categories", [])
        genre_categories = categories_context.get("genre_categories", [])

        category_choices = [(name, name) for name in (language_categories + genre_categories)]

        # Form に POST を入れて検証
        form = ReviewCreateForm(
            data=request.POST,
            category_choices=category_choices,
        )

        # NGなら、同じ画面に戻す
        if not form.is_valid():
            context = self.get_context_data(**kwargs)

            # POST時はここで上書き（エラー内容をテンプレに渡す）
            context["form"] = form
            context["posted_categories"] = request.POST.getlist("categories")
            context["posted_rating"] = request.POST.get("rating", "")

            return render(request, self.template_name, context)

        # OKなら clean済みデータを取り出す
        cleaned = form.cleaned_data
        rating = cleaned["rating"]
        categories = cleaned["categories"]
        review_title = cleaned["review_title"]
        review_text = cleaned["review_text"]
        study_flow_enabled = cleaned.get("study_flow_enabled", False)

        # 本来ここでDB保存して review_id を作る
        dummy_review_id = "dummy"

        # 二重投稿防止で本選択sessionを消す
        pop_selected_book_from_session(request.session)

        print("cleaned rating:", rating)
        print("cleaned categories:", categories)
        print("cleaned title:", review_title)
        print("cleaned text:", review_text)
        print("study_flow_enabled:", study_flow_enabled)

        # 完了ページへリダイレクト
        complete_url = f"{reverse('reviews:complete')}?review_id={dummy_review_id}"
        return redirect(complete_url)


def review_complete(request):
    # 投稿完了ページ
    review_id = request.GET.get("review_id", "dummy")
    return render(request, "reviews/review_complete.html", {"review_id": review_id})


def review_detail(request, book_id: str, review_id: int):
    # サービスから context を受け取って描画するだけ
    context = build_review_detail_context(book_id, review_id)
    return render(request, "reviews/layout/review_detail.html", context)


@require_POST
def review_like_toggle(request, book_id: str, review_id: int):
    # いいねトグル（ログイン/未ログイン両対応）
    # ログイン済み: user=request.user を使う
    # 未ログイン: cookie の anon_key を使う（なければ発行）

    # ログインしてるか判定
    is_auth = request.user.is_authenticated

    # 未ログインなら anon_key を用意
    anon_key = None
    should_set_cookie = False

    if not is_auth:
        # cookie から anon_key を探す
        anon_key = request.COOKIES.get("anon_key")

        if not anon_key:
            #  無ければ作る（URL安全なランダム文字列）
            # 64文字に収める（DBがmax_length=64）
            anon_key = secrets.token_urlsafe(48)[:64]
            should_set_cookie = True

    # サービスにどっちの識別子かを渡す
    result = toggle_like_db(
        user=request.user if is_auth else None,
        anon_key=anon_key if not is_auth else None,
        book_id=book_id,
        review_id=review_id,
    )

    # not found
    if not result.get("ok") and result.get("status") == 404:
        return JsonResponse(
            {"ok": False, "message": result.get("message", "not found")},
            status=404,
        )

    # cookie をセットする必要があればレスポンスに付ける
    response = JsonResponse(result)

    if should_set_cookie:
        # cookie を保存（未ログインいいねの識別に使う）
        # max_age: 180日
        response.set_cookie(
            "anon_key",
            anon_key,
            max_age=60 * 60 * 24 * 180,
            httponly=True,
            samesite="Lax",
        )

    return response