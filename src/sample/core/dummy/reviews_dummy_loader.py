import json
from django.conf import settings


def load_reviews_dummy() -> dict:
    # reviews_dummy.json を読み込んで dict で返す
    json_path = settings.BASE_DIR / "core" / "dummy" / "reviews_dummy.json"
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_book(data: dict, book_id: str) -> dict | None:
    # books から book_id が一致するものを1件探す
    books = data.get("books", [])
    return next((b for b in books if b.get("book_id") == book_id), None)


def list_reviews_by_book(data: dict, book_id: str) -> list[dict]:
    # reviews_review から book_id が一致するレビューだけ返す
    all_reviews = data.get("reviews_review", [])
    return [r for r in all_reviews if r.get("book_id") == book_id]


def find_review(data: dict, review_id: int) -> dict | None:
    # reviews_review から id が一致するレビューを1件探す
    all_reviews = data.get("reviews_review", [])
    return next((r for r in all_reviews if int(r.get("id", 0)) == int(review_id)), None)


def list_flows_by_review(data: dict, review_id: int) -> list[dict]:
    # flows から review_id が一致するものを position 昇順で返す
    flows = data.get("flows", [])
    result = [f for f in flows if int(f.get("review_id", 0)) == int(review_id)]
    return sorted(result, key=lambda x: int(x.get("position", 0)))


def count_likes(data: dict, review_id: int) -> int:
    # review_goods の件数 = いいね数（DBの代わり）
    # review_goods が無い場合でも落ちないようにする
    goods = data.get("review_goods", [])
    return len([g for g in goods if int(g.get("review_id", 0)) == int(review_id)])


def get_user_name(data: dict, user_id: int) -> str:
    # users から user_id の name を返す
    # 見つからない場合は空文字
    users = data.get("users", [])
    u = next((x for x in users if int(x.get("user_id", 0)) == int(user_id)), None)
    return u.get("name", "") if u else ""


def enrich_review_ui(data: dict, review: dict) -> dict:
    # rating を float にする
    try:
        rating = float(review.get("rating", 0))
    except (TypeError, ValueError):
        rating = 0.0

    full_count = int(rating)
    has_half = (rating - full_count) >= 0.5

    if "ui" not in review or not isinstance(review["ui"], dict):
        review["ui"] = {}

    # 星表示用
    review["ui"]["full_stars"] = list(range(full_count))
    review["ui"]["has_half_star"] = has_half

    # user_name
    user_name = get_user_name(data, review.get("user_id", 0))
    if user_name:
        review["ui"]["user_name"] = user_name

    # likes_count
    calculated_likes = count_likes(data, review.get("id", 0))
    if calculated_likes > 0:
        review["ui"]["likes_count"] = calculated_likes
    else:
        review["ui"]["likes_count"] = int(review["ui"].get("likes_count", 0) or 0)

    # has_flow
    flows = list_flows_by_review(data, review.get("id", 0))
    if len(flows) > 0:
        review["ui"]["has_flow"] = True
    else:
        review["ui"]["has_flow"] = bool(review["ui"].get("has_flow", False))

    return review