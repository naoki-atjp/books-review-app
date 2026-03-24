# 責務：
# ログイン処理
# マイページ表示（GET）
# 編集保存（POST）：いまはDB保存はなし。入力チェックとトーストだけ整える

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from users.forms import EmailAuthenticationForm, UserEditForm
from users.services.mypage_context_service import build_mypage_context
from users.services.user_dummy_service import load_user_dummy 


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    next_url = request.GET.get("next") or request.POST.get("next") or ""
    form = EmailAuthenticationForm(request=request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            auth_login(request, form.get_user())

            redirect_to = next_url
            if redirect_to and url_has_allowed_host_and_scheme(
                url=redirect_to,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(redirect_to)

            return redirect(settings.LOGIN_REDIRECT_URL)

        for err in form.non_field_errors():
            messages.error(request, err)

    return render(
        request,
        "registration/login.html",
        {
            "form": form,
            "next_url": next_url,
        },
    )


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
