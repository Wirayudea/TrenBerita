from typing import List


def generate_title_from_keywords(keywords: List[str], max_words: int = 8) -> str:
    if not keywords:
        return "Berita Tren Viral"
    selected = keywords[:max_words]
    return " ".join(w.capitalize() for w in selected)
