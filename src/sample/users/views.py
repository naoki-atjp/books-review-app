# 責務：
# マイページ表示（GET）
# 編集保存（POST）：いまはDB保存はなし。入力チェックとトーストだけ整える

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users.services.user_dummy_service import load_user_dummy 
from users.forms import UserEditForm
from users.services.mypage_context_service import build_mypage_context

@login_required
def mypage_view(request):
    is_edit = request.GET.get("mode") == "edit"

    # POST（保存）
    if request.method == "POST":
        # 保存失敗したら編集画面に留めたいので is_edit=True
        is_edit = True

        form = UserEditForm(request.POST, user=request.user)

        # まず context を作る（テンプレに渡す土台）
        context = build_mypage_context(
            request_user=request.user,
            is_edit=is_edit,
            form=form,
        )

        if not form.is_valid():
            # フォーム全体エラーをトーストに載せる
            for err in form.errors.get("__all__", []):
                messages.error(request, err)

            # パスワードはリセット
            # 入力クリア
            context["form"] = UserEditForm(
                initial={"name": request.user.name, "email": request.user.email},
                user=request.user,
            )
            return render(request, "users/layout/mypage.html", context)

        messages.success(request, "プロフィールが更新されました")
        return redirect("users:mypage")

    # GET（表示）
    form = UserEditForm(
        initial={"name": request.user.name, "email": request.user.email},
        user=request.user,
    )

    context = build_mypage_context(
        request_user=request.user,
        is_edit=is_edit,
        form=form,
    )
    return render(request, "users/layout/mypage.html", context)