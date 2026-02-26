import re
from typing import List

import nltk
from nltk.corpus import stopwords


# Pastikan di awal kamu sudah menjalankan download stopwords sekali saja:
# >>> import nltk
# >>> nltk.download("stopwords")

try:
    _INDONESIAN_STOPWORDS = set(stopwords.words("indonesian"))
except LookupError:
    # Fallback sederhana jika korpus stopwords belum terinstall
    _INDONESIAN_STOPWORDS = {
        "yang",
        "dan",
        "di",
        "ke",
        "dari",
        "untuk",
        "dengan",
        "pada",
        "ini",
        "itu",
        "atau",
        "juga",
        "karena",
        "sebagai",
        "ada",
        "tidak",
        "iya",
        "saja",
        "akan",
        "bagi",
    }


def tokenize(text: str) -> List[str]:
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    tokens = text.split()
    tokens = [t for t in tokens if t not in _INDONESIAN_STOPWORDS and len(t) > 2]
    return tokens


def preprocess(text: str) -> str:
    return " ".join(tokenize(text))
