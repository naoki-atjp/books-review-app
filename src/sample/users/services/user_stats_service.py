# 責務：
# マイページの統計情報(stats)を返す責務を集める
# DB接続のタイミングで、DB版の関数に差し替える

from __future__ import annotations
from typing import Dict

from users.services.user_dummy_service import load_user_dummy

def get_user_stats_dummy() -> Dict[str, int]:
    # ダミーJSONから stats を返す
    user_data = load_user_dummy()
    stats = user_data.get("stats", {}) or {}

    # もしキーが無くても落ちないように default を入れる
    return {
        "review_count": int(stats.get("review_count", 0)),
        "like_count": int(stats.get("like_count", 0)),
        "flow_count": int(stats.get("flow_count", 0)),
    }