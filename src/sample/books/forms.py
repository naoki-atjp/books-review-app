#責務：
# Viewで受け取る入力（GET/POST）をバリデーションする
# 「空白除去」「型変換」「最低限の制約（min_value等）」をここで保証
# 画面表示のロジックや外部API呼び出しは書かない

from django import forms
from .models import Category

class CategoryForm(forms.ModelForm):

  class Meta:
    model = Category
    fields = ["category_code", "category_name"]

class BookSearchForm(forms.Form):
    # 空ワード検索は無効
    q = forms.CharField(required=False)

    # ページ番号
    page = forms.IntegerField(required=False, min_value=1)

    # form内の不要な余白は除外
    def clean_q(self):
        q = (self.cleaned_data.get("q") or "").strip()
        return q