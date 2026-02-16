from books.services.category_provider import load_categories

def get_categories_for_view() -> dict:
    # views はこの関数だけ使う
    return load_categories()