import json
from pathlib import Path

from django.conf import settings
from django.templatetags.static import static


def load_user_dummy() -> dict:
    # 仮データの値は JSON にのみ置く
    # Python側は「読み込み」と「URL整形」だけ行う
    dummy_path = Path(settings.BASE_DIR) / "core" / "dummy" / "user_dummy.json"

    if not dummy_path.exists():
        raise FileNotFoundError(f"Dummy JSON not found: {dummy_path}")

    with dummy_path.open("r", encoding="utf-8") as f:
        user_data = json.load(f)

    icon_path = user_data.get("icon_path")

    if icon_path:
        # 例: "img/insect.svg" -> "/static/img/insect.svg"
        user_data["icon_url"] = static(icon_path)
    else:
        user_data["icon_url"] = static("img/user_icon.svg")

    return user_data