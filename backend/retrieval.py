import faiss
import pickle
from pathlib import Path
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent
VECTORSTORE_PATH = BASE_DIR / "vectorstore"


# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


index = None
metadata = []


def load_vector_database():
    global index, metadata

    index = faiss.read_index(
        str(VECTORSTORE_PATH / "index.faiss")
    )

    with open(VECTORSTORE_PATH / "metadata.pkl", "rb") as f:
        metadata = pickle.load(f)

    print("Vector database loaded.")
    print("FAISS vectors:", index.ntotal)
    print("Metadata entries:", len(metadata))


# Load vector database when the application starts
load_vector_database()


def retrieve_documents(query, top_k=5):

    # --------------------------------
    # 1. Semantic vector search
    # --------------------------------

    query_embedding = model.encode([query])

    search_k = min(top_k * 10, index.ntotal)

    distances, indices = index.search(
        query_embedding,
        search_k
    )

    results = []
    seen_chunks = set()

    for i in range(search_k):

        index_position = indices[0][i]

        if index_position == -1:
            continue

        chunk_text = metadata[index_position]["text"]

        # Avoid duplicate chunks
        if chunk_text in seen_chunks:
            continue

        seen_chunks.add(chunk_text)

        results.append({
            "text": chunk_text,
            "source": metadata[index_position]["source"],
            "distance": float(distances[0][i])
        })

        if len(results) == top_k:
            break


    # --------------------------------
    # 2. Keyword fallback
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


    # Sort keyword matches by relevance
    keyword_results.sort(
        key=lambda x: x["keyword_score"],
        reverse=True
    )


    # Add keyword matches
    for result in keyword_results:

        if result["text"] not in seen_chunks:

            results.append(result)
            seen_chunks.add(result["text"])


    # Keep only required number of results
    results = results[:top_k]


    # --------------------------------
    # 3. Display retrieved documents
    # --------------------------------

    print("\nRetrieved documents:")

    for result in results:

        print(
            f"Source: {result['source']} | "
            f"Distance: {result['distance']:.4f}"
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