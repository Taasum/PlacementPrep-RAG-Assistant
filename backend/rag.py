from retrieval import retrieve_documents
from llm import generate_answer


def ask_rag(question , subject="All Subjects"):

    results = retrieve_documents(
        question,
        top_k=3,
        threshold=1.5
    )

    # No relevant documents found
    if not results:
        return (
            "I could not find this information in the uploaded "
            "study material.",
            []
        )

    context_parts = []

    for result in results:

        context_parts.append(
            f"Source: {result['source']}\n"
            f"{result['text']}"
        )

    context = "\n\n".join(context_parts)

    answer = generate_answer(
        question,
        context
    )

    return answer, results


if __name__ == "__main__":

    question = input("Ask your question: ")

    answer, sources = ask_rag(question)

    print("\n===== ANSWER =====\n")
    print(answer)

    print("\n===== SOURCES =====\n")

    for source in sources:
        print(
            source["source"],
            "| Distance:",
            source["distance"]
        )