import json
from django.conf import settings

def load_categories() -> dict:
    # DB接続まではJSON
    json_path = settings.BASE_DIR / "core" / "dummy" / "categories_dummy.json"
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

    # 将来はここをDB取得に置き換える