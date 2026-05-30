from pathlib import Path

try:
    from pdf_reader import extract_text_from_pdf
    from rag import PDF_DIR, split_text
    from vector_store import add_chunks
except ImportError:
    from backend.pdf_reader import extract_text_from_pdf
    from backend.rag import PDF_DIR, split_text
    from backend.vector_store import add_chunks


def index_pdf(file_path: Path) -> dict:
    pages = extract_text_from_pdf(file_path)
    chunks = []

    for page in pages:
        for chunk_index, chunk in enumerate(split_text(page["text"])):
            chunks.append(
                {
                    "text": chunk,
                    "document_name": file_path.name,
                    "page_number": page["page_number"],
                    "chunk_index": chunk_index,
                }
            )

    if chunks:
        add_chunks(chunks)

    return {"document": file_path.name, "pages": len(pages), "chunks": len(chunks)}


def index_dataset() -> list[dict]:
    results = []
    for file_path in sorted(PDF_DIR.glob("*.pdf")):
        results.append(index_pdf(file_path))
    return results


if __name__ == "__main__":
    for result in index_dataset():
        print(
            f"{result['document']}: "
            f"{result['pages']} readable pages, {result['chunks']} chunks indexed"
        )
