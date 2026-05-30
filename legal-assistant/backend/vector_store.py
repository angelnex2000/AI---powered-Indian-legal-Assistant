import json
from pathlib import Path
from uuid import uuid4

import numpy as np
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent.parent
VECTOR_DB_DIR = BASE_DIR / "vector_db"
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
FALLBACK_STORE = VECTOR_DB_DIR / "fallback_store.json"

model = SentenceTransformer("all-MiniLM-L6-v2")


def _load_chroma_collection():
    try:
        import chromadb

        client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
        return client.get_or_create_collection(name="legal_docs")
    except Exception:
        return None


collection = _load_chroma_collection()


def add_chunks(chunks: list[dict]) -> None:
    records = []

    for chunk in chunks:
        text = chunk["text"]
        embedding = model.encode(text).tolist()
        records.append(
            {
                "id": uuid4().hex,
                "text": text,
                "embedding": embedding,
                "metadata": {
                    "document_name": chunk["document_name"],
                    "page_number": chunk["page_number"],
                    "chunk_index": chunk["chunk_index"],
                },
            }
        )

    if collection is not None:
        collection.add(
            ids=[record["id"] for record in records],
            documents=[record["text"] for record in records],
            embeddings=[record["embedding"] for record in records],
            metadatas=[record["metadata"] for record in records],
        )
        return

    existing = _read_fallback_records()
    existing.extend(records)
    FALLBACK_STORE.write_text(json.dumps(existing), encoding="utf-8")


def search_chunks(query: str, n_results: int = 3) -> list[dict]:
    query_embedding = model.encode(query).tolist()

    if collection is not None:
        if collection.count() == 0:
            return []
        results = collection.query(query_embeddings=[query_embedding], n_results=n_results)
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        return [
            {
                "text": document,
                "document_name": metadata.get("document_name", "Unknown document"),
                "page_number": metadata.get("page_number", "Unknown"),
                "distance": distance,
            }
            for document, metadata, distance in zip(documents, metadatas, distances)
        ]

    return _search_fallback(query_embedding=query_embedding, n_results=n_results)


def _read_fallback_records() -> list[dict]:
    if not FALLBACK_STORE.exists():
        return []
    return json.loads(FALLBACK_STORE.read_text(encoding="utf-8"))


def _search_fallback(query_embedding: list[float], n_results: int) -> list[dict]:
    records = _read_fallback_records()
    if not records:
        return []

    query_vector = np.array(query_embedding)
    scored = []

    for record in records:
        vector = np.array(record["embedding"])
        score = float(
            np.dot(query_vector, vector)
            / (np.linalg.norm(query_vector) * np.linalg.norm(vector))
        )
        scored.append((score, record))

    scored.sort(key=lambda item: item[0], reverse=True)

    return [
        {
            "text": record["text"],
            "document_name": record["metadata"].get("document_name", "Unknown document"),
            "page_number": record["metadata"].get("page_number", "Unknown"),
            "distance": 1 - score,
        }
        for score, record in scored[:n_results]
    ]
