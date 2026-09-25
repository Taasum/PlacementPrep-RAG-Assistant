import faiss
import pickle

from pathlib import Path
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent
VECTORSTORE_PATH = BASE_DIR / "vectorstore"

model = SentenceTransformer("all-MiniLM-L6-v2")


index = faiss.read_index(
    str(VECTORSTORE_PATH / "index.faiss")
)

with open(
    VECTORSTORE_PATH / "metadata.pkl",
    "rb"
) as f:

    metadata = pickle.load(f)


def retrieve_documents(query, top_k=3, threshold=1.5):

    query_embedding = model.encode([query])

    distances, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for i in range(top_k):

        index_position = indices[0][i]

        if index_position == -1:
            continue

        distance = float(distances[0][i])

        # Ignore chunks that are too dissimilar
        if distance > threshold:
            continue

        results.append({
            "text": metadata[index_position]["text"],
            "source": metadata[index_position]["source"],
            "distance": distance
        })

    return results


if __name__ == "__main__":

    question = input("Ask your question: ")

    results = retrieve_documents(question)

    print("\nRetrieved Documents:\n")

    if not results:

        print("No sufficiently relevant documents found.")

    else:

        for i, result in enumerate(results):

            print(f"--- Result {i + 1} ---")

            print("Source:", result["source"])

            print("Distance:", result["distance"])

            print("Text:")

            print(result["text"])

            print()