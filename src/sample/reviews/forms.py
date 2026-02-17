# 責務:
# レビュー投稿フォームのバリデーションをまとめる
# views.py は「Formを使ってOKなら次へ、NGなら画面に戻す」だけにする

from django import forms
from decimal import Decimal, InvalidOperation

class ReviewCreateForm(forms.Form):
  # 必須項目
  rating = forms.CharField(
      required=True,
      error_messages={"required": "※評価を選択してください。"}
  )
  review_title = forms.CharField(
      required=True,
      max_length=100,
      error_messages={"required": "※レビュータイトルを入力してください。"}
  )
  review_text = forms.CharField(
      required=True,
      widget=forms.Textarea,
      error_messages={"required": "※レビュー本文を入力してください。"}
  )
  categories = forms.MultipleChoiceField(
      required=True,
      error_messages={"required": "※カテゴリを1つ以上選択してください。"}
  )
  recommended_for = forms.CharField(
    required=True,
    widget=forms.Textarea,
    error_messages={"required": "※おすすめする人を入力してください。"}
)

  # 学習フロー（任意）
  study_flow_enabled = forms.BooleanField(required=False)

  def __init__(self, *args, **kwargs):
    category_choices = kwargs.pop("category_choices", [])
    super().__init__(*args, **kwargs)

    # choicesは (value, label) のタプル配列
    self.fields["categories"].choices = category_choices


  def clean_rating(self):
    #ratingが0.5刻み & 規定範囲内かチェック
    raw = self.cleaned_data["rating"]

    # 文字列 → Decimal に変換（安全に数値比較できる）
    try:
      rating = Decimal(raw)
    except InvalidOperation:
      raise forms.ValidationError("評価は数値で入力してください。")

    if rating < Decimal("0.5") or rating > Decimal("5.0"):
      raise forms.ValidationError("評価は 0.5〜5.0 の範囲で選択してください。")
    
    if (rating * 2) % 1 != 0:
      raise forms.ValidationError("評価は 0.5〜5.0 の範囲で選択してください。")
    
    return rating
  
  def clean_review_title(self):
    # 空文字やスペースだけを弾く
    title = self.cleaned_data["review_title"].strip()
    if not title:
        raise forms.ValidationError("※レビュータイトルを入力してください。")
    return title

  def clean_review_text(self):
    # 空文字やスペースだけを弾く
    text = self.cleaned_data["review_text"].strip()
    if not text:
        raise forms.ValidationError("※レビュー本文を入力してください。")
    return text

