# 責務：
# マイページ表示（GET）
# 編集保存（POST）：いまはDB保存はなし。入力チェックとトーストだけ整える

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users.services.user_dummy_service import load_user_dummy 
from users.services.mypage_reviews_service import list_my_reviews_for_mypage
from users.forms import UserEditForm

@login_required
def mypage_view(request):
    is_edit = request.GET.get("mode") == "edit"

    # JSONは service で読む（viewsに仮データは置かない方針）
    user_data = load_user_dummy()

    # ダミー上は user_id=1 のレビューが「佐藤太郎」なので仮で設定
    # TODO: request.user.id に置き換える
    my_reviews = list_my_reviews_for_mypage(user_id=1)

    context = {
        "user": request.user,
        "user_data": user_data,
        "my_reviews": my_reviews,
        # GETならURLから決める/POSTなら編集画面のまま
        "is_edit": request.GET.get("mode") == "edit",
        "form": None,
    }

    # POST（保存ボタンが押された時）
    if request.method == "POST":
        # POSTの戻りは編集画面のまま
        context["is_edit"] = True

        form = UserEditForm(request.POST, user=request.user)
        context["form"] = form 

        if not form.is_valid():
            for err in form.errors.get("__all__", []):
                messages.error(request, err)

            context["form"] = None
            # 画面は編集モードに戻す
            return render(request, "users/layout/mypage.html", context)

        messages.success(request, "プロフィールが更新されました")

        # 編集モードを閉じて戻す
        return redirect("users:mypage")

    # GET（表示）
    context["form"] = UserEditForm(
        initial={
            "name": request.user.name,
            "email": request.user.email,
        },
        user=request.user,
    )

    return render(request, "users/layout/mypage.html", context)