import json
from pathlib import Path

from django.conf import settings
from django.templatetags.static import static
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from users.services.user_dummy_service import load_user_dummy 
from users.services.mypage_reviews_service import list_my_reviews_for_mypage

@login_required
def mypage_view(request):
    is_edit = request.GET.get("mode") == "edit"

    # JSONは service で読む（viewsに仮データは置かない方針）
    user_data = load_user_dummy()

    # ダミー上は user_id=1 のレビューが「佐藤太郎」なので仮で設定
    my_reviews = list_my_reviews_for_mypage(user_id=1)

    context = {
        "user": request.user,   # ログイン中のユーザー情報
        "user_data": user_data, # マイページ上部UI用
        "is_edit": is_edit,     # include切替用
        "my_reviews": my_reviews,
    }

    return render(request, "users/layout/mypage.html", context)


def mypage(request):
    # JSON仮データの読み込み
    dummy_path = Path(settings.BASE_DIR) / "core" / "dummy" / "user_dummy.json"

    user_data = {
        "name": "未設定ユーザー",
        "email": "unknown@example.com",
        "registered_date": "---- -- --",
        "icon_url": "",
        "stats": {"review_count": 0, "like_count": 0, "flow_count": 0},
    }

    if dummy_path.exists():
        with dummy_path.open("r", encoding="utf-8") as f:
            user_data = json.load(f)

    is_edit = request.GET.get("mode") == "edit"

    icon_url = user_data.get("icon_url")
    if not icon_url:
        icon_url = static("img/user_icon.svg")

    context = {
        "user_data": user_data,
        "icon_url": icon_url,
        "is_edit": is_edit,
    }

    return render(request, "user/mypage.html", context)