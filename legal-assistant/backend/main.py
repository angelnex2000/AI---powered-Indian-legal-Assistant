from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

try:
    from rag import ask_question, process_pdf, process_topic
except ImportError:
    from backend.rag import ask_question, process_pdf, process_topic


app = FastAPI(
    title="AI-Powered Indian Legal Assistant API",
    description="Simple RAG API for uploaded Indian legal PDFs.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "AI Legal Assistant API is running"}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    result = await process_pdf(file)
    return result


@app.post("/ask")
def ask(query: str = Form(...), language: Optional[str] = Form("english")):
    if not query.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    return ask_question(query=query, language=language or "english")


@app.post("/topic")
def add_topic(topic: str = Form(...)):
    return process_topic(topic)
