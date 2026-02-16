#責務：
# カテゴリ一覧の「取得方法」を集約する差し替えポイント
# 現在：JSONから読む
# 将来：DB取得（またはAPI）へ差し替える
# 画面用の整形は categories.py 側でやり、providerは取得に専念する

import json
from django.conf import settings
from typing import Any, Dict

def load_categories() -> Dict[str, Any]:
    # ============================
    # views/services から呼ぶ
    # DB接続まではJSON から読み込む
    # DB接続時この中身だけ差し替え
    # ============================
    return _load_from_json()

def _load_from_json() -> Dict[str, Any]:
    # ============================
    # JSONからカテゴリデータを読み込む
    # ============================

    json_path = settings.BASE_DIR / "core" / "dummy" / "categories_dummy.json"

    # ファイルを開いて読み込む
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data