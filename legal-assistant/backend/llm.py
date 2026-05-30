import os


LEGAL_DISCLAIMER = "This is general legal information, not legal advice. Consult a qualified lawyer."


def _fallback_answer(query: str, context: str, language: str) -> str:
    language_note = "Hindi" if language.lower() == "hindi" else "English"
    direct_answer = _direct_simple_answer(query=query, context=context, language=language)
    if direct_answer:
        return direct_answer

    return (
        f"Based on the uploaded document, here are the most relevant parts I found.\n\n"
        f"Question: {query}\n\n"
        f"Simple explanation ({language_note}):\n"
        f"{context}\n\n"
        f"{LEGAL_DISCLAIMER}"
    )


def _direct_simple_answer(query: str, context: str, language: str) -> str:
    query_lower = query.lower()
    context_lower = context.lower()

    if "mrp" in query_lower or "maximum retail price" in query_lower:
        if "maximum retail price" in context_lower or "mrp" in context_lower:
            if language.lower() == "hindi":
                return (
                    "Simple Answer (Hindi):\n"
                    "Agar koi shopkeeper packaged product par printed MRP se zyada paisa leta hai, "
                    "toh aap bill maang sakte hain aur overcharging ki complaint kar sakte hain. "
                    "Aap consumer helpline ya consumer commission me complaint karke refund/compensation "
                    "maang sakte hain.\n\n"
                    f"{LEGAL_DISCLAIMER}"
                )

            return (
                "Simple Answer (English):\n"
                "If a seller charges more than the printed MRP for a packaged product, it can be treated "
                "as overcharging or an unfair trade practice. Ask for a proper bill, keep proof of payment, "
                "and complain to the consumer helpline or consumer commission. You may ask for refund, "
                "compensation, or correction of the unfair practice.\n\n"
                f"{LEGAL_DISCLAIMER}"
            )

    fraud_words = ["online fraud", "cyber fraud", "report fraud", "scam", "upi", "otp", "phishing"]
    if any(word in query_lower for word in fraud_words):
        if "cybercrime.gov.in" in context_lower or "1930" in context_lower:
            if language.lower() == "hindi":
                return (
                    "Simple Answer (Hindi):\n"
                    "Online fraud report karne ke liye turant National Cyber Crime Portal "
                    "cybercrime.gov.in par complaint file karein ya cyber fraud helpline 1930 par call karein. "
                    "Screenshots, transaction ID, phone number, website link, bank SMS, email, aur chat records "
                    "save rakhein. Agar paisa gaya hai, toh apne bank/payment app ko bhi turant inform karein.\n\n"
                    f"{LEGAL_DISCLAIMER}"
                )

            return (
                "Simple Answer (English):\n"
                "To report online fraud in India, file a complaint on the National Cyber Crime Portal "
                "at cybercrime.gov.in or call the cyber fraud helpline 1930 as soon as possible. "
                "Keep screenshots, transaction IDs, phone numbers, website links, bank messages, emails, "
                "and chat records as proof. If money was deducted, also contact your bank or payment app "
                "immediately and ask them to block or hold the transaction.\n\n"
                f"{LEGAL_DISCLAIMER}"
            )

    property_words = [
        "land",
        "property",
        "plot",
        "occupy",
        "occupied",
        "acquire",
        "acquired",
        "accuire",
        "encroach",
        "grab",
        "possession",
        "trespass",
    ]
    if any(word in query_lower for word in property_words):
        if "land or property dispute" in context_lower or "encroaches" in context_lower:
            if language.lower() == "hindi":
                return (
                    "Simple Answer (Hindi):\n"
                    "Agar koi aapki zameen par kabza ya encroachment kar raha hai, toh pehle apne documents "
                    "collect karein: sale deed/title deed, tax receipt, mutation/patta/khata, survey map, photos "
                    "aur witnesses. Force use na karein. Local police me complaint karein agar trespass, threat, "
                    "force ya land grabbing hai. Revenue office me land measurement/record correction ke liye "
                    "application de sakte hain. Property lawyer ke through legal notice bhejkar civil court me "
                    "injunction, possession, ya encroachment removal ka case file kiya ja sakta hai.\n\n"
                    f"{LEGAL_DISCLAIMER}"
                )

            return (
                "Simple Answer (English):\n"
                "If someone has occupied, encroached on, or is claiming your land, first collect proof: "
                "sale deed/title deed, tax receipts, mutation/patta/khata records, survey map, photos, "
                "videos, and witness details. Do not use force. If there is trespass, threat, force, or "
                "land grabbing, file a police complaint. You can also approach the revenue office for land "
                "measurement or record correction. Through a local property lawyer, you may send a legal "
                "notice and file a civil case for injunction, possession, declaration of title, or removal "
                "of encroachment.\n\n"
                f"{LEGAL_DISCLAIMER}"
            )

    return ""


def generate_answer(query: str, context: str, language: str = "english") -> str:
    provider = os.getenv("LLM_PROVIDER", "").lower().strip()

    if provider == "openai" and os.getenv("OPENAI_API_KEY"):
        return _openai_answer(query=query, context=context, language=language)

    if provider == "gemini" and os.getenv("GEMINI_API_KEY"):
        return _gemini_answer(query=query, context=context, language=language)

    return _fallback_answer(query=query, context=context, language=language)


def _system_prompt(language: str) -> str:
    output_language = "Hindi" if language.lower() == "hindi" else "English"
    return (
        "You are an AI-powered Indian legal assistant. Answer only from the provided context. "
        "Explain in simple words, mention uncertainty when the context is insufficient, "
        f"write in {output_language}, and always include that this is not legal advice."
    )


def _openai_answer(query: str, context: str, language: str) -> str:
    from openai import OpenAI

    client = OpenAI()
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": _system_prompt(language)},
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion:\n{query}",
            },
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content or ""


def _gemini_answer(query: str, context: str, language: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))
    response = model.generate_content(
        f"{_system_prompt(language)}\n\nContext:\n{context}\n\nQuestion:\n{query}"
    )
    return response.text
