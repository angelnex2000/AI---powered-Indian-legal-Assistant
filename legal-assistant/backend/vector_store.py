import json
import math
import re
from collections import Counter
from pathlib import Path
from uuid import uuid4


BASE_DIR = Path(__file__).resolve().parent.parent
VECTOR_DB_DIR = BASE_DIR / "vector_db"
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
FALLBACK_STORE = VECTOR_DB_DIR / "fallback_store.json"

TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")


def add_chunks(chunks: list[dict]) -> None:
    records = _read_records()

    for chunk in chunks:
        text = chunk["text"]
        records.append(
            {
                "id": uuid4().hex,
                "text": text,
                "tokens": _token_counts(text),
                "metadata": {
                    "document_name": chunk["document_name"],
                    "page_number": chunk["page_number"],
                    "chunk_index": chunk["chunk_index"],
                },
            }
        )

    FALLBACK_STORE.write_text(json.dumps(records), encoding="utf-8")


def search_chunks(query: str, n_results: int = 3) -> list[dict]:
    records = _read_records()
    if not records:
        return []

    query_tokens = _token_counts(query)
    scored = []

    for record in records:
        score = _cosine_similarity(query_tokens, record["tokens"])
        if score <= 0:
            continue
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


def _read_records() -> list[dict]:
    if not FALLBACK_STORE.exists():
        return []
    records = json.loads(FALLBACK_STORE.read_text(encoding="utf-8"))

    for record in records:
        if "tokens" not in record:
            record["tokens"] = _token_counts(record.get("text", ""))

    return records


def _token_counts(text: str) -> dict[str, int]:
    tokens = [token.lower() for token in TOKEN_RE.findall(text)]
    return dict(Counter(tokens))


def _cosine_similarity(left: dict[str, int], right: dict[str, int]) -> float:
    common_tokens = set(left).intersection(right)
    dot_product = sum(left[token] * right[token] for token in common_tokens)

    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))

    if left_norm == 0 or right_norm == 0:
        return 0.0

    return dot_product / (left_norm * right_norm)
