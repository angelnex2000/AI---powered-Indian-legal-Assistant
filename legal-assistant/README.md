# AI-Powered Indian Legal Assistant using RAG

A simple RAG-based legal assistant for Indian legal PDFs. Users upload a PDF, the backend extracts and chunks text, stores embeddings in ChromaDB, retrieves relevant chunks, and returns a simple answer with document/page sources.

> Disclaimer: This app gives general legal information, not professional legal advice. Consult a qualified lawyer.

## Features

- Upload Indian legal PDFs such as Constitution notes, consumer rights notes, rental agreements, legal notices, and employment agreements.
- Extract text page by page using `pypdf`.
- Chunk extracted text for retrieval.
- Create embeddings with `sentence-transformers`.
- Store vectors in ChromaDB.
- Ask questions against uploaded documents.
- Show source document and page number.
- Optional OpenAI or Gemini answer generation.
- Basic Hindi answer mode.

## Project Structure

```text
legal-assistant/
├── backend/
│   ├── main.py
│   ├── rag.py
│   ├── pdf_reader.py
│   ├── vector_store.py
│   ├── llm.py
│   └── requirements.txt
├── frontend/
│   ├── app.py
│   └── requirements.txt
├── data/
│   └── legal_pdfs/
├── vector_db/
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## Run Locally

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r backend\requirements.txt -r frontend\requirements.txt
```

Start the backend:

```powershell
cd backend
uvicorn main:app --reload
```

Open the API docs:

```text
http://127.0.0.1:8000/docs
```

Start the frontend in another terminal:

```powershell
cd frontend
streamlit run app.py
```

Open Streamlit:

```text
http://127.0.0.1:8501
```

## Optional LLM Setup

The app works as a retrieval demo without an API key. To enable generated simple answers, create a `.env` file from `.env.example`.

For OpenAI:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

For Gemini:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-1.5-flash
```

## Run with Docker

Create a `.env` file first:

```powershell
copy .env.example .env
```

Then run:

```powershell
docker compose up --build
```

Backend:

```text
http://127.0.0.1:8000/docs
```

Frontend:

```text
http://127.0.0.1:8501
```

## Best Dataset Topics

- Indian Constitution basics
- Consumer Protection Act notes
- Cyber crime awareness notes
- RTI Act notes
- Rental agreement sample
- Legal notice sample
- Employment agreement sample

## Important Note

This project is for learning and demonstration. It should not be used as a replacement for professional legal advice.
