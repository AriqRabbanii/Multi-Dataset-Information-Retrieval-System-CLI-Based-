import re
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

factory = StemmerFactory()
stemmer = factory.create_stemmer()

STOPWORDS = {
    "yang", "dan", "di", "ke", "dari", "untuk",
    "pada", "adalah", "dengan", "dalam", "ini",
    "itu", "atau", "juga", "akan", "dapat",
    "merupakan", "sebagai", "secara", "oleh",
    "karena", "agar", "sudah", "telah", "tidak",
    "bisa", "lebih", "sangat", "suatu"
}


_stem_cache = {}


def preprocess(text):
    if not text:
        return ""

    # 1. Case folding
    text = text.lower()

    # 2. Tokenization: hanya mengambil kata dan angka
    tokens = re.findall(r"\b[a-zA-Z0-9]+\b", text)

    # 3. Stopword removal
    tokens = [
        word for word in tokens
        if word not in STOPWORDS
    ]

    # 4. Stemming bahasa Indonesia dengan caching untuk performa tinggi
    stemmed_tokens = []
    for word in tokens:
        if word.isdigit():
            stemmed_tokens.append(word)
            continue
        if word not in _stem_cache:
            _stem_cache[word] = stemmer.stem(word)
        stemmed_tokens.append(_stem_cache[word])

    return " ".join(stemmed_tokens)

