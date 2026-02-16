#責務：
# テンプレで使うカテゴリ一覧を返す窓口
# Viewは get_categories_for_view() だけ呼べばOKにする
# データ取得の実体（JSON/DB/API）は provider 側に隠蔽する

from books.services.category_provider import load_categories

def get_categories_for_view() -> dict:
    # views はこの関数だけ使う
    return load_categories()