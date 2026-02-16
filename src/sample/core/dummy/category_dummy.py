#責務：
# 開発中（DB/API未接続）のための「カテゴリ仮データ読み込み」を提供する
# categories_dummy.json を読み込み、dictとして返すだけの役割にする

#方針：
# ViewやServiceはこのファイルの中身（パスやjson.load）を意識しない
# 将来カテゴリをDB/APIから取得するようになったら、このファイルは削除または未使用にする
# books/services/category_provider.py 側にDB取得処理が移る）

import json
from django.conf import settings

def get_category_context() -> dict:
    json_path = settings.BASE_DIR / "core" / "dummy" / "categories_dummy.json"
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)