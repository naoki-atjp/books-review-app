from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Category
from .forms import CategoryForm

@login_required
def category_list(request):
  categories = Category.objects.all().order_by("category_code")
  return render(
    request,
    "books/category_list.html",
    {"categories": categories},
  )

@login_required
def category_create(request):
  if request.method == "POST":
    form = CategoryForm(request.POST)
    if form.is_valid():
      category = form.save(commit=False)   # ① まだDBには保存しない
      category.created_by = request.user   # ② 作成者をログイン中ユーザーに
      category.updated_by = request.user   # ③ 更新者も同じユーザーでOK
      category.save()                      # ④ ここで初めてINSERT
      return redirect("category_list")
  else:
    form = CategoryForm()

  return render(
    request,
    "books/category_form.html",
    {"form": form},
  )

@login_required
def category_update(request, pk):
  category = get_object_or_404(Category, pk=pk)
  if request.method == "POST":
    form = CategoryForm(request.POST, instance=category)
    if form.is_valid():
      category = form.save(commit=False)   # ① いったんインスタンスだけ取得
      category.updated_by = request.user   # ② 更新した人を記録
      category.save()                      # ③ UPDATE
      return redirect("category_list")
  else:
    form = CategoryForm(instance=category)
  return render(
      request,
      "books/category_form.html",
      {"form": form},
    )
  
@login_required
def category_delete(request, pk):
  category = get_object_or_404(Category, pk=pk)

  if request.method == "POST":
    category.delete()
    return redirect("category_list")
  
  return render(
    request,
    "books/category_confirm_delete.html",
    {"category": category}
  )