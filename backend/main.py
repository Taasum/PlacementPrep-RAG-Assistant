from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ingestion import add_pdf_to_vector_database
from rag import ask_rag
import os
import shutil


app = FastAPI(title="PlacementPrep RAG Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ "http://localhost:5173",
        "http://localhost:5175",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str
    subject: str = "All Subjects"


@app.get("/")
def home():
    return {
        "message": "PlacementPrep RAG Assistant API is running"
    }


@app.post("/ask")
def ask_question(request: QuestionRequest):

    answer, sources = ask_rag(request.question , request.subject)

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
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        return {
            "message": "Only PDF files are supported."
        }

    upload_dir = "../documents/uploads"
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(
        upload_dir,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        chunk_count = add_pdf_to_vector_database(
            file_path
        )

        return {
            "message": "PDF uploaded and indexed successfully.",
            "filename": file.filename,
            "chunks_added": chunk_count
        }

    except Exception as e:
        return {
            "message": "PDF uploaded but indexing failed.",
            "error": str(e)
        }