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