import os
import pickle
from pathlib import Path

from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer


BASE_DIR = Path(__file__).resolve().parent
DOCUMENTS_PATH = BASE_DIR.parent / "knowledge_base"
VECTORSTORE_PATH = BASE_DIR / "vectorstore"


def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def create_chunks(text, chunk_size=1000, overlap=200):
    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk.strip())

        start += chunk_size - overlap

    return chunks


def create_vector_database():

    all_chunks = []
    metadata = []

    for root, dirs, files in os.walk(DOCUMENTS_PATH):

        for file in files:

            if file.lower().endswith(".pdf"):

                file_path = os.path.join(root, file)

                print(f"Processing: {file}")

                text = extract_text_from_pdf(file_path)

                chunks = create_chunks(text)

                for chunk in chunks:

                    all_chunks.append(chunk)

                    metadata.append({
                        "source": file,
                        "text": chunk
                    })

    print("Total chunks:", len(all_chunks))

    if not all_chunks:
        raise ValueError("No PDF content found.")

    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    vectors = vectorizer.fit_transform(all_chunks)

    VECTORSTORE_PATH.mkdir(exist_ok=True)

    # Save TF-IDF vectorizer
    with open(
        VECTORSTORE_PATH / "vectorizer.pkl",
        "wb"
    ) as f:

        pickle.dump(vectorizer, f)

    # Save document vectors
    with open(
        VECTORSTORE_PATH / "vectors.pkl",
        "wb"
    ) as f:

        pickle.dump(vectors, f)

    # Save metadata
    with open(
        VECTORSTORE_PATH / "metadata.pkl",
        "wb"
    ) as f:

        pickle.dump(metadata, f)

    print("TF-IDF vector database created successfully!")


def add_pdf_to_vector_database(file_path):

    print(f"Processing uploaded PDF: {file_path}")

    text = extract_text_from_pdf(file_path)

    if not text.strip():

        raise ValueError(
            "No text could be extracted from the PDF."
        )

    chunks = create_chunks(
        text,
        chunk_size=1000,
        overlap=200
    )

    if not chunks:

        raise ValueError(
            "No usable chunks were created."
        )

    # Load existing data
    with open(
        VECTORSTORE_PATH / "metadata.pkl",
        "rb"
    ) as f:

        metadata = pickle.load(f)

    # Add new chunks
    for chunk in chunks:

        metadata.append({
            "source": os.path.basename(file_path),
            "text": chunk
        })

    # Rebuild TF-IDF database with all chunks
    all_texts = [
        item["text"]
        for item in metadata
    ]

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    vectors = vectorizer.fit_transform(
        all_texts
    )

    # Save everything
    with open(
        VECTORSTORE_PATH / "vectorizer.pkl",
        "wb"
    ) as f:

        pickle.dump(vectorizer, f)

    with open(
        VECTORSTORE_PATH / "vectors.pkl",
        "wb"
    ) as f:

        pickle.dump(vectors, f)

    with open(
        VECTORSTORE_PATH / "metadata.pkl",
        "wb"
    ) as f:

        pickle.dump(metadata, f)

    print(
        f"Added {len(chunks)} chunks from "
        f"{os.path.basename(file_path)}"
    )

    return len(chunks)


if __name__ == "__main__":

    create_vector_database()