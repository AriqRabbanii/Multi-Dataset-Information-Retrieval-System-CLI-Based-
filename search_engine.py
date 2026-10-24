from whoosh.qparser import QueryParser
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from indexing import get_index
from preprocessing import preprocess


def search_documents(query, top_n=5):
    """Mencari dokumen berdasarkan query menggunakan Whoosh untuk temu kembali kandidat

    dan CountVectorizer + Cosine Similarity untuk perangkingan kemiripan dokumen.
    Mengembalikan 5 dokumen teratas dengan skor tertinggi sesuai instruksi teknis.
    """
    # Preprocessing query
    processed_query = preprocess(query)

    if not processed_query.strip():
        print("Query tidak memiliki kata yang dapat dicari.")
        return []

    ix = get_index()

    with ix.searcher() as searcher:
        # Pencarian kandidat menggunakan Whoosh
        parser = QueryParser("processed", schema=ix.schema)
        parsed_query = parser.parse(processed_query)

        results = searcher.search(parsed_query, limit=100)

        if not results:
            return []

        # Mengambil data kandidat dokumen
        candidates = []

        for result in results:
            candidates.append({
                "id": result["doc_id"],
                "source": result.get("source", "-"),
                "title": result["title"],
                "content": result["content"],
                "processed": result["processed"]
            })

    # Membuat representasi vektor CountVectorizer untuk query dan kandidat dokumen
    corpus = [processed_query] + [
        doc["processed"] for doc in candidates
    ]

    vectorizer = CountVectorizer(
        tokenizer=str.split,
        preprocessor=None,
        token_pattern=None,
        lowercase=False
    )

    count_matrix = vectorizer.fit_transform(corpus)

    # Menghitung Cosine Similarity antara vektor query dan seluruh kandidat dokumen
    query_vector = count_matrix[0:1]
    document_vectors = count_matrix[1:]

    scores = cosine_similarity(
        query_vector,
        document_vectors
    ).flatten()

    # Menambahkan skor kemiripan ke setiap dokumen kandidat
    for i, score in enumerate(scores):
        candidates[i]["score"] = float(score)

    # Ranking dari skor tertinggi ke terendah
    candidates.sort(
        key=lambda doc: doc["score"],
        reverse=True
    )

    # Mengembalikan 5 dokumen teratas sesuai spesifikasi instruksi teknis
    return candidates[:top_n]
