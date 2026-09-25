from pathlib import Path
import os
import shutil

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ingestion import add_pdf_to_vector_database
from rag import ask_rag
from retrieval import load_vector_database


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

FRONTEND_DIST = BASE_DIR.parent / "frontend" / "dist"

UPLOAD_DIR = BASE_DIR.parent / "documents" / "uploads"


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="PlacementPrep RAG Assistant"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5175",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# REQUEST MODEL
# =========================================================

class QuestionRequest(BaseModel):
    question: str
    subject: str = "All Subjects"


# =========================================================
# ASK QUESTION
# =========================================================

@app.post("/ask")
def ask_question(request: QuestionRequest):

    answer, sources = ask_rag(
        request.question,
        request.subject
    )

    return {
        "question": request.question,
        "answer": answer,
        "sources": [
            {
                "file": source["source"],
                "distance": source["distance"],
                "snippet": source["text"][:300]
            }
            for source in sources
        ]
    }


# =========================================================
# UPLOAD PDF
# =========================================================

@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...)
):

    # Check file type
    if not file.filename.lower().endswith(".pdf"):
        return {
            "message": "Only PDF files are supported."
        }

    # Create upload directory
    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save uploaded file
    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    try:

        # Add PDF chunks and embeddings to FAISS
        chunk_count = add_pdf_to_vector_database(
            str(file_path)
        )

        # IMPORTANT:
        # Reload the updated FAISS index and metadata
        load_vector_database()

        print("\n================================")
        print("PDF UPLOAD SUCCESSFUL")
        print("File:", file.filename)
        print("Chunks added:", chunk_count)
        print("FAISS database reloaded")
        print("================================\n")

        return {
            "message": "PDF uploaded and indexed successfully.",
            "filename": file.filename,
            "chunks_added": chunk_count
        }

    except Exception as e:

        print("PDF indexing error:", e)

        return {
            "message": "PDF uploaded but indexing failed.",
            "error": str(e)
        }


# =========================================================
# FRONTEND
# =========================================================

# Serve React static assets
if FRONTEND_DIST.exists():

    app.mount(
        "/assets",
        StaticFiles(
            directory=FRONTEND_DIST / "assets"
        ),
        name="assets"
    )


# =========================================================
# SERVE REACT APP
# =========================================================

@app.get("/")
def serve_home():

    return FileResponse(
        FRONTEND_DIST / "index.html"
    )


@app.get("/{full_path:path}")
def serve_frontend(full_path: str):

    file_path = FRONTEND_DIST / full_path

    if file_path.is_file():

        return FileResponse(
            file_path
        )

    return FileResponse(
        FRONTEND_DIST / "index.html"
    )