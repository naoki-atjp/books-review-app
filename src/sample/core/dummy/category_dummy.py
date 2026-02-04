from typing import List, Dict


def get_category_context() -> Dict[str, List[str]]:

    # 言語・フレームワークのカテゴリ
    language_categories: List[str] = [
        "JavaScript",
        "TypeScript",
        "Python",
        "Java",
        "C言語",
        "C++",
        "C#",
        "PHP",
        "Ruby",
        "Flutter",
        "Kotlin",
        "Swift",
        "React",
    ]

    # ジャンルのカテゴリ
    genre_categories: List[str] = [
        "開発・設計",
        "アーキテクチャ",
        "データ・AI",
        "セキュリティ",
        "キャリア",
        "仕事術",
        "マインド",
        "学習法",
        "インフラ・クラウド",
        "品質・テスト",
    ]

    # テンプレートで使うキー名
    return {
        "language_categories": language_categories,
        "genre_categories": genre_categories,
    }