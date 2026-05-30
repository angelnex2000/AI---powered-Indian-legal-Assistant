from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

try:
    from llm import generate_answer
    from pdf_reader import extract_text_from_pdf
    from vector_store import add_chunks, search_chunks
except ImportError:
    from backend.llm import generate_answer
    from backend.pdf_reader import extract_text_from_pdf
    from backend.vector_store import add_chunks, search_chunks


BASE_DIR = Path(__file__).resolve().parent.parent
PDF_DIR = BASE_DIR / "data" / "legal_pdfs"
PDF_DIR.mkdir(parents=True, exist_ok=True)

TOPIC_NOTES = {
    "bail": """
    Bail means temporary release of an arrested person from custody, usually with conditions.
    The person may need to give a bond or surety and must appear before the court when required.
    Bail does not mean the person is declared innocent. It only allows release while the case continues.
    In bailable offences, bail is generally a right. In non-bailable offences, the court decides after
    considering the facts, seriousness of the offence, risk of absconding, and possibility of tampering
    with evidence.
    """,
    "consumer_rights": """
    Consumer rights in India protect buyers of goods and services from unfair trade practices,
    defective goods, deficient services, misleading advertisements, and overcharging.
    A seller should not charge more than the printed Maximum Retail Price, also called MRP,
    for a packaged product. Charging above MRP can be treated as an unfair trade practice
    or overcharging. A consumer can ask for a proper bill, complain to consumer helpline,
    file a complaint before the appropriate consumer commission, and may seek refund,
    compensation, or correction of the unfair practice.
    """,
    "cyber_crime": """
    Online fraud or cyber fraud includes scams such as UPI fraud, fake shopping websites,
    phishing links, OTP scams, fake job offers, identity theft, and unauthorised bank
    transactions. In India, a person can report online fraud on the National Cyber Crime
    Reporting Portal at cybercrime.gov.in or call the cyber fraud helpline 1930 as soon as
    possible. The complainant should keep screenshots, transaction IDs, phone numbers,
    website links, bank messages, emails, and any chat records as evidence. For money fraud,
    the person should also contact the bank or payment app quickly and ask them to block or
    hold the transaction if possible.
    """,
    "property_dispute": """
    A land or property dispute may happen when another person occupies, encroaches on,
    grabs, sells, blocks access to, or claims ownership over someone else's land. The owner
    should first collect land records and proof such as sale deed, title deed, patta or khata,
    property tax receipts, mutation records, survey map, possession proof, photos, videos,
    and witness details. The owner can send a legal notice, complain to the local police if
    there is trespass, force, threat, or land grabbing, approach revenue authorities for land
    measurement or correction of records, and file a civil suit for injunction, declaration,
    possession, or removal of encroachment. The owner should avoid using force and should
    consult a local property lawyer because land laws and revenue procedures differ by state.
    """,
    "rental_agreement": """
    A rental agreement records the terms between landlord and tenant. Important clauses include rent,
    security deposit, lock-in period, notice period, maintenance responsibility, permitted use of the
    property, termination conditions, renewal terms, and dispute resolution. Both parties should read
    these clauses carefully before signing.
    """,
    "legal_notice": """
    A legal notice is a formal written communication that informs another person about a legal claim,
    demand, or grievance. It usually states the facts, the legal issue, the action demanded, and a time
    limit for response. It is often sent before filing a court case or complaint.
    """,
    "constitution_basics": """
    The Constitution of India is the supreme law of India. It explains the structure of government,
    fundamental rights, directive principles, duties, and the powers of the legislature, executive, and
    judiciary. Fundamental rights protect citizens against unlawful state action and support equality,
    liberty, and constitutional remedies.
    """,
}

TOPIC_KEYWORDS = {
    "consumer_rights": [
        "consumer",
        "mrp",
        "maximum retail price",
        "overcharge",
        "overcharging",
        "extra",
        "refund",
        "defective",
        "shop",
        "seller",
        "bill",
    ],
    "cyber_crime": [
        "online fraud",
        "cyber fraud",
        "fraud",
        "scam",
        "upi",
        "otp",
        "phishing",
        "cyber",
        "1930",
        "bank fraud",
        "report fraud",
    ],
    "property_dispute": [
        "land",
        "property",
        "plot",
        "field",
        "house",
        "occupy",
        "occupied",
        "acquire",
        "acquired",
        "accuire",
        "encroach",
        "encroachment",
        "grab",
        "land grabbing",
        "possession",
        "trespass",
        "title deed",
        "sale deed",
    ],
    "bail": ["bail", "arrest", "custody", "surety", "bailable", "non-bailable"],
    "rental_agreement": ["rent", "rental", "tenant", "landlord", "deposit", "notice period"],
    "legal_notice": ["legal notice", "notice", "demand", "reply notice"],
    "constitution_basics": ["constitution", "fundamental right", "article", "equality", "liberty"],
}


def split_text(text: str, chunk_size: int = 900, overlap: int = 150) -> list[str]:
    clean_text = " ".join(text.split())
    if not clean_text:
        return []

    chunks = []
    step = max(chunk_size - overlap, 1)

    for start in range(0, len(clean_text), step):
        chunk = clean_text[start : start + chunk_size]
        if chunk.strip():
            chunks.append(chunk)

    return chunks


async def process_pdf(file: UploadFile) -> dict:
    safe_name = Path(file.filename or "uploaded.pdf").name
    file_path = PDF_DIR / f"{uuid4().hex}_{safe_name}"

    file_bytes = await file.read()
    file_path.write_bytes(file_bytes)

    pages = extract_text_from_pdf(file_path)
    chunks = []

    for page in pages:
        for chunk_index, chunk in enumerate(split_text(page["text"])):
            chunks.append(
                {
                    "text": chunk,
                    "document_name": safe_name,
                    "page_number": page["page_number"],
                    "chunk_index": chunk_index,
                }
            )

    if not chunks:
        return {
            "message": "PDF uploaded, but no readable text was found.",
            "document": safe_name,
            "chunks": 0,
        }

    add_chunks(chunks)

    return {
        "message": "PDF processed successfully.",
        "document": safe_name,
        "pages": len(pages),
        "chunks": len(chunks),
    }


def process_topic(topic: str) -> dict:
    topic_key = topic.strip().lower()
    text = TOPIC_NOTES.get(topic_key)

    if not text:
        return {
            "message": "Unknown topic. Please choose one of the available topics.",
            "chunks": 0,
        }

    chunks = [
        {
            "text": chunk,
            "document_name": f"Built-in topic: {topic_key.replace('_', ' ').title()}",
            "page_number": 1,
            "chunk_index": index,
        }
        for index, chunk in enumerate(split_text(text, chunk_size=700, overlap=80))
    ]

    add_chunks(chunks)

    return {
        "message": "Topic notes processed successfully.",
        "document": topic_key,
        "chunks": len(chunks),
    }


def ask_question(query: str, language: str = "english") -> dict:
    results = search_chunks(query=query, n_results=4)
    results = _filter_relevant_results(results)

    built_in_results = _find_builtin_topic_results(query)
    if built_in_results:
        results = _merge_results(built_in_results, results)

    if not results:
        return {
            "answer": (
                "I could not find relevant content for this question. Please upload a related PDF "
                "or choose a matching sample law topic first."
            ),
            "sources": [],
            "disclaimer": "This is not legal advice. Consult a qualified lawyer.",
        }

    context = "\n\n".join(
        f"Source {i + 1} ({item['document_name']}, page {item['page_number']}):\n{item['text']}"
        for i, item in enumerate(results)
    )

    answer = generate_answer(query=query, context=context, language=language)

    sources = [
        {
            "document_name": item["document_name"],
            "page_number": item["page_number"],
            "text": item["text"][:450],
        }
        for item in results
    ]

    return {
        "answer": answer,
        "sources": sources,
        "disclaimer": "This is not legal advice. Consult a qualified lawyer.",
    }


def _filter_relevant_results(results: list[dict]) -> list[dict]:
    relevant = []
    for item in results:
        distance = item.get("distance")
        if distance is None or distance <= 0.75:
            relevant.append(item)
    return relevant


def _find_builtin_topic_results(query: str) -> list[dict]:
    query_lower = query.lower()
    matches = []

    for topic, keywords in TOPIC_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in query_lower)
        if score == 0:
            continue

        matches.append((score, topic))

    if not matches:
        return []

    matches.sort(reverse=True)
    score, topic = matches[0]
    text = " ".join(TOPIC_NOTES[topic].split())

    return [
        {
            "text": text,
            "document_name": f"Built-in topic: {topic.replace('_', ' ').title()}",
            "page_number": 1,
            "distance": 0.0,
            "keyword_score": score,
        }
    ]


def _merge_results(primary: list[dict], secondary: list[dict]) -> list[dict]:
    seen = set()
    merged = []

    for item in primary + secondary:
        key = (item.get("document_name"), item.get("page_number"), item.get("text"))
        if key in seen:
            continue
        seen.add(key)
        merged.append(item)

    return merged[:4]
