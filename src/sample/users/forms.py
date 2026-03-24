# 責務：
# マイページ編集（ユーザー名/メール/パスワード変更）の入力チェックを担当
# Viewはフォームを呼んでOK/NGを判断するだけにする

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()


class EmailAuthenticationForm(AuthenticationForm):
    # ログイン画面専用フォーム
    # username ではなく email でログインできるようにする

    username = forms.EmailField(
        required=True,
        label="メールアドレス",
        widget=forms.EmailInput(
            attrs={
                "class": "w-full rounded-[14px] border border-[#D9D9D9] bg-[#F5F5F5] px-4 py-3 text-[15px] text-[#333333] placeholder:text-[#9A9A9A] outline-none transition focus:border-[#1565E5] focus:bg-white",
                "placeholder": "メールアドレスを入力",
                "autocomplete": "email",
            }
        ),
        error_messages={
            "required": "メールアドレスを入力してください。",
            "invalid": "正しいメールアドレス形式で入力してください。",
        },
    )

    password = forms.CharField(
        required=True,
        label="パスワード",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full rounded-[14px] border border-[#D9D9D9] bg-[#F5F5F5] px-4 py-3 text-[15px] text-[#333333] outline-none transition focus:border-[#1565E5] focus:bg-white",
                "placeholder": "パスワードを入力",
                "autocomplete": "current-password",
            }
        ),
        error_messages={
            "required": "パスワードを入力してください。",
        },
    )

    error_messages = {
        "invalid_login": "メールアドレスまたはパスワードが正しくありません。",
        "inactive": "このアカウントは無効です。",
    }

    def clean(self):
        # AuthenticationForm は username フィールド名を前提に持っているため、
        # 画面上は email 入力でも内部では username という名前で受け取る
        email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if email and password:
            # まず email からユーザーを探す
            user = User.objects.filter(email__iexact=email).first()

            # 該当ユーザーが見つかった場合は、その username を使って認証する
            auth_username = user.get_username() if user else email

            self.user_cache = authenticate(
                self.request,
                username=auth_username,
                password=password,
            )

            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages["invalid_login"],
                    code="invalid_login",
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class UserEditForm(forms.Form):
    # プロフィール（名前/メール）
    name = forms.CharField(
        required=True,
        max_length=30,
        label="ユーザー名",
    )

    email = forms.EmailField(
        required=True,
        max_length=255,
        label="メールアドレス",
    )

    # パスワード
    current_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
        label="現在のパスワード",
    )

    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
        label="新しいパスワード",
    )

    new_password_confirm = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
        label="新しいパスワード（確認）",
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._user = user

    def clean(self):
        # パスワード変更の整合性をてチェックする
        cleaned = super().clean()

        current = cleaned.get("current_password") or ""
        new = cleaned.get("new_password") or ""
        confirm = cleaned.get("new_password_confirm") or ""

        # 何も入ってないならパスワード変更しない
        if current == "" and new == "" and confirm == "":
            return cleaned

        # どれかだけ入ってるのはNG（3つセットで必要）
        if not current or not new or not confirm:
            raise forms.ValidationError("パスワード変更には「現在/新しい/確認」をすべて入力してください。")

        # 新しいPWと確認が一致するか
        if new != confirm:
            raise forms.ValidationError("パスワードが一致していません。")

        # 半角英数字だけ
        if not new.isalnum():
            raise forms.ValidationError("パスワードは半角英数字のみで入力してください。")

        # 現在PWが正しいかチェック
        if self._user and hasattr(self._user, "check_password"):
            if not self._user.check_password(current):
                raise forms.ValidationError("現在のパスワードが正しくありません。")

        return cleaned