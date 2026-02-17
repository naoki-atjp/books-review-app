# 責務：
# マイページ編集（ユーザー名/メール/パスワード変更）の入力チェックを担当
# Viewはフォームを呼んでOK/NGを判断するだけにする

from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


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