import json
from django.conf import settings
import copy


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
    # reviewを直接書き換えない
    # UI表示用の情報は付加した結果を返す

    # 元のreviewを壊さないようにshallow copy
    r = copy.deepcopy(review)

    # ratingをfloatにする
    try:
        rating = float(r.get("rating", 0))
    except (TypeError, ValueError):
        rating = 0.0

    full_count = int(rating)
    has_half = (rating - full_count) >= 0.5

    # ui が無い/壊れてても必ず dict を用意
    base_ui = r.get("ui")
    if not isinstance(base_ui, dict):
        base_ui = {}

    # ここで作るuiを完成形として上書き
    ui = {}

    ui["full_stars"] = list(range(full_count))  # 例：3なら [0,1,2]
    ui["has_half_star"] = has_half
    ui["user_name"] = get_user_name(data, r.get("user_id", 0))
    ui["likes_count"] = count_likes(data, r.get("id", 0))
    flows = list_flows_by_review(data, r.get("id", 0))
    ui["has_flow"] = len(flows) > 0

    r["ui"] = ui
    return r


def find_review_by_book(data: dict, book_id: str, review_id: int) -> dict | None:
    # review_idで探す
    # そのreviewが URL のbook_idと一致するか確認する
    review = find_review(data, review_id)
    if not review:
        return None

    # book_id が一致しないなら見つからない扱い
    if review.get("book_id") != book_id:
        return None

    return review


def get_review_detail_context(data: dict, book_id: str, review_id: int) -> dict:
    # review_detail.html に渡す context をここで完成させる
    book = find_book(data, book_id)
    if not book:
        return {
            "not_found": True,
            "book": {"book_id": book_id},
            "review": {"review_id": review_id},
            "flows": [],
        }

    review = find_review_by_book(data, book_id, review_id)
    if not review:
        return {
            "not_found": True,
            "book": book,
            "review": {"review_id": review_id},
            "flows": [],
        }

    # ui を付加
    enriched_review = enrich_review_ui(data, review)

    flows = list_flows_by_review(data, review_id)

    return {
        "not_found": False,
        "book": book,
        "review": enriched_review,
        "flows": flows,
    }