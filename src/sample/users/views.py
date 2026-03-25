# 責務：
# ログイン処理
# マイページ表示（GET）
# 編集保存（POST）：いまはDB保存はなし。入力チェックとトーストだけ整える

import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from users.forms import EmailAuthenticationForm, SignupForm, UserEditForm
from users.services.mypage_context_service import build_mypage_context
from users.services.user_dummy_service import load_user_dummy 

User = get_user_model()


def _generate_internal_username():
    while True:
        username = f"user_{uuid.uuid4().hex}"
        if not User.objects.filter(username=username).exists():
            return username


def csrf_failure_view(request, reason=""):
    if request.path == "/users/signup/":
        messages.error(request, "ページの有効期限が切れました。もう一度入力してアカウントを作成してください。")
        return redirect("users:signup")

    if request.path == "/accounts/login/":
        messages.error(request, "ページの有効期限が切れました。もう一度ログインしてください。")
        return redirect("login")

    if request.path == "/users/logout/":
        messages.error(request, "操作を完了できませんでした。もう一度お試しください。")
        return redirect(settings.LOGOUT_REDIRECT_URL)

    return render(request, "403.html", status=403)


@never_cache
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


@never_cache
def signup_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = SignupForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        try:
            user = User.objects.create_user(
                username=_generate_internal_username(),
                email=form.cleaned_data["email"],
                name=form.cleaned_data["name"],
                password=form.cleaned_data["password1"],
            )
        except IntegrityError:
            form.add_error("email", "このメールアドレスは既に登録されています。")
        else:
            auth_login(request, user)
            return redirect("home")

    return render(
        request,
        "registration/signup.html",
        {
            "form": form,
        },
    )


@require_POST
def logout_view(request):
    auth_logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)

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
