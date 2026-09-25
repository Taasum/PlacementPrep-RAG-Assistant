import os
import pickle
import faiss
from embeddings import get_model
from pathlib import Path
from pypdf import PdfReader



# Project paths
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
    model = get_model()
    embeddings = model.encode(all_chunks)

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    VECTORSTORE_PATH.mkdir(exist_ok=True)

    faiss.write_index(
        index,
        str(VECTORSTORE_PATH / "index.faiss")
    )

    with open(
        VECTORSTORE_PATH / "metadata.pkl",
        "wb"
    ) as f:

        pickle.dump(metadata, f)

    print("Vector database created successfully!")


def add_pdf_to_vector_database(file_path):

    print(f"Processing uploaded PDF: {file_path}")

    # 1. Extract text
    text = extract_text_from_pdf(file_path)

    if not text.strip():
        raise ValueError(
            "No text could be extracted from the PDF."
        )

    # 2. Create chunks
    chunks = create_chunks(
        text,
        chunk_size=1000,
        overlap=200
    )

    if not chunks:
        raise ValueError(
            "No usable chunks were created."
        )

    # 3. Create embeddings
    model = get_model()
    embeddings = model.encode(chunks)

    # 4. Load existing FAISS index
    index = faiss.read_index(
        str(VECTORSTORE_PATH / "index.faiss")
    )

    # 5. Add new embeddings
    index.add(embeddings)

    # 6. Load existing metadata
    with open(
        VECTORSTORE_PATH / "metadata.pkl",
        "rb"
    ) as f:

        metadata = pickle.load(f)

    # 7. Add metadata
    for chunk in chunks:

        metadata.append({
            "source": os.path.basename(file_path),
            "text": chunk
        })

    # 8. Save updated FAISS index
    faiss.write_index(
        index,
        str(VECTORSTORE_PATH / "index.faiss")
    )

    # 9. Save updated metadata
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