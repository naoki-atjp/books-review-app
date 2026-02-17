# 責務：
# mypageに必要なデータ（user_data / stats / my_reviews）をまとめて作る
# views.pyはこの関数を呼んでrenderする

from __future__ import annotations
from typing import Any, Dict

from users.services.user_dummy_service import load_user_dummy
from users.services.user_stats_service import get_user_stats_dummy
from users.services.mypage_reviews_service import list_my_reviews_for_mypage

def build_mypage_context(*, request_user, is_edit: bool, form) -> Dict[str, Any]:
    # マイページに必要な context をまとめて返す

    # ユーザー基本情報（今はdummy）
    user_data = load_user_dummy()

    # stats（今はdummy）
    user_data["stats"] = get_user_stats_dummy()

    # 自分のレビュー一覧（今はdummy）
    # TODO: dummyの user_id=1 を request_user.id に寄せる
    my_reviews = list_my_reviews_for_mypage(user_id=1)

    return {
        "user": request_user,
        "user_data": user_data,
        "my_reviews": my_reviews,
        "is_edit": is_edit,
        "form": form,
    }