from retrieval import retrieve_documents
from llm import generate_answer


def ask_rag(question, subject="All Subjects"):

    # Retrieve the most relevant chunks
    results = retrieve_documents(
        question,
        top_k=5
    )

    # If nothing was retrieved
    if not results:
        return (
            "I could not find this information in the uploaded "
            "study material.",
            []
        )

    # Build context from retrieved chunks
    context_parts = []

    for result in results:
        context_parts.append(
            f"Source: {result['source']}\n"
            f"{result['text']}"
        )

    context = "\n\n".join(context_parts)

    # Generate answer using Groq
    answer = generate_answer(
        question,
        context
    )

    return answer, results