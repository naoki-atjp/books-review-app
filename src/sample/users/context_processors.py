from users.services.user_dummy_service import load_user_dummy


def header_user_context(request):
    # ログインしていない時は none（ヘッダーで分岐）
    if not request.user.is_authenticated:
        return {"header_user_data": None}

    # ログインしている時だけ、仮データを渡す (仮)
    return {"header_user_data": load_user_dummy()}