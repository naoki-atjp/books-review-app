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
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import (
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.core.mail import send_mail
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.utils.encoding import force_bytes, force_str
from django.utils.http import url_has_allowed_host_and_scheme, urlsafe_base64_decode, urlsafe_base64_encode

from users.forms import EmailAuthenticationForm, ResendVerificationEmailForm, SignupForm, UserEditForm
from users.services.mypage_context_service import build_mypage_context
from users.services.user_dummy_service import load_user_dummy

User = get_user_model()


class AnonymousOnlyMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)


def _generate_internal_username():
    while True:
        username = f"user_{uuid.uuid4().hex}"
        if not User.objects.filter(username=username).exists():
            return username


def _send_signup_verification_email(request, user):
    verify_url = request.build_absolute_uri(
        reverse(
            "users:verify_email",
            kwargs={
                "uidb64": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user),
            },
        )
    )
    subject = render_to_string("users/signup/verification_subject.txt").strip()
    message = render_to_string(
        "users/signup/verification_email.txt",
        {
            "user": user,
            "verify_url": verify_url,
        },
    )
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )


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
    show_resend_verification_link = False

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

        show_resend_verification_link = form.has_unverified_email_error()
        for err in form.non_field_errors():
            messages.error(request, err)

    return render(
        request,
        "registration/login.html",
        {
            "form": form,
            "next_url": next_url,
            "show_resend_verification_link": show_resend_verification_link,
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
            _send_signup_verification_email(request, user)
            return redirect("users:signup_verification_sent")

    return render(
        request,
        "users/signup/form.html",
        {
            "form": form,
        },
    )


@never_cache
def signup_verification_sent_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    return render(request, "users/signup/verification_sent.html")


@never_cache
def resend_verification_email_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = ResendVerificationEmailForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = User.objects.filter(email__iexact=form.cleaned_data["email"]).first()
        if user and not user.is_email_verified:
            _send_signup_verification_email(request, user)
        return redirect("users:resend_verification_email_done")

    return render(
        request,
        "users/email_verification/resend.html",
        {"form": form},
    )


@never_cache
def resend_verification_email_done_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    return render(request, "users/email_verification/resend_done.html")


@never_cache
def verify_email_view(request, uidb64, token):
    user = None

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if not user.is_email_verified:
            user.is_email_verified = True
            user.save(update_fields=["is_email_verified"])

        return render(
            request,
            "users/signup/verification_complete.html",
            {"is_success": True},
        )

    return render(
        request,
        "users/signup/verification_complete.html",
        {"is_success": False},
        status=400,
    )


class PasswordResetRequestView(AnonymousOnlyMixin, PasswordResetView):
    template_name = "registration/password_reset/request.html"
    email_template_name = "registration/password_reset/email.txt"
    subject_template_name = "registration/password_reset/subject.txt"
    success_url = reverse_lazy("users:password_reset_done")


class PasswordResetDonePageView(AnonymousOnlyMixin, PasswordResetDoneView):
    template_name = "registration/password_reset/done.html"


class PasswordResetConfirmPageView(PasswordResetConfirmView):
    template_name = "registration/password_reset/confirm.html"
    success_url = reverse_lazy("password_reset_complete")


class PasswordResetCompletePageView(PasswordResetCompleteView):
    template_name = "registration/password_reset/complete.html"


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
