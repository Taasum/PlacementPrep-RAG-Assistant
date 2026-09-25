import pickle
from pathlib import Path

from sklearn.metrics.pairwise import cosine_similarity


BASE_DIR = Path(__file__).resolve().parent
VECTORSTORE_PATH = BASE_DIR / "vectorstore"


vectorizer = None
vectors = None
metadata = []


def load_vector_database():

    global vectorizer, vectors, metadata

    with open(
        VECTORSTORE_PATH / "vectorizer.pkl",
        "rb"
    ) as f:

        vectorizer = pickle.load(f)

    with open(
        VECTORSTORE_PATH / "vectors.pkl",
        "rb"
    ) as f:

        vectors = pickle.load(f)

    with open(
        VECTORSTORE_PATH / "metadata.pkl",
        "rb"
    ) as f:

        metadata = pickle.load(f)

    print("TF-IDF vector database loaded.")

    print(
        "Total vectors:",
        vectors.shape[0]
    )

    print(
        "Metadata entries:",
        len(metadata)
    )


# Load database when application starts
load_vector_database()


def retrieve_documents(query, top_k=5):

    # --------------------------------
    # 1. Convert query into TF-IDF vector
    # --------------------------------

    query_vector = vectorizer.transform([query])

    # --------------------------------
    # 2. Calculate cosine similarity
    # --------------------------------

    similarities = cosine_similarity(
        query_vector,
        vectors
    )[0]

    # Get indices sorted by similarity
    ranked_indices = similarities.argsort()[::-1]

    results = []

    seen_chunks = set()

    # --------------------------------
    # 3. Retrieve relevant chunks
    # --------------------------------

    for index_position in ranked_indices:

        score = similarities[index_position]

        chunk_text = metadata[index_position]["text"]

        # Avoid duplicate chunks
        if chunk_text in seen_chunks:
            continue

        seen_chunks.add(chunk_text)

        # Ignore completely unrelated chunks
        if score <= 0:
            continue

        results.append({
            "text": chunk_text,
            "source": metadata[index_position]["source"],
            "distance": float(1 - score)
        })

        if len(results) == top_k:
            break

    # --------------------------------
    # 4. Keyword fallback
    # --------------------------------

    query_words = set(
        query.lower()
        .replace("?", "")
        .split()
    )

    keyword_results = []

    for item in metadata:

        text_lower = item["text"].lower()

        score = 0

        for word in query_words:

            if len(word) >= 3 and word in text_lower:
                score += 1

        if score >= 2:

            if item["text"] not in seen_chunks:

                keyword_results.append({
                    "text": item["text"],
                    "source": item["source"],
                    "distance": 0.0,
                    "keyword_score": score
                })

    keyword_results.sort(
        key=lambda x: x["keyword_score"],
        reverse=True
    )

    # Add keyword matches
    for result in keyword_results:

        if result["text"] not in seen_chunks:

            results.append(result)

            seen_chunks.add(result["text"])

    # Keep only top_k results
    results = results[:top_k]

    # --------------------------------
    # 5. Display retrieved documents
    # --------------------------------

    print("\nRetrieved documents:")

    for result in results:

        print(
            f"Source: {result['source']} | "
            f"Score/Distance: {result['distance']:.4f}"
        )

        print(
            "Text:",
            result["text"][:300].replace("\n", " ")
        )

        print()

    return results


# --------------------------------
# Test retrieval directly
# --------------------------------

if __name__ == "__main__":

    retrieve_documents(
        "How many DSA problems have I solved according to my resume?",
        top_k=5
    )