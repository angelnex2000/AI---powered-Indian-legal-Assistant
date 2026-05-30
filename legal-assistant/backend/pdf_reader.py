from pathlib import Path
from typing import Union

from pypdf import PdfReader


def extract_text_from_pdf(file_path: Union[str, Path]) -> list[dict]:
    reader = PdfReader(str(file_path))
    pages = []

    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append({"page_number": index, "text": text})

    return pages
