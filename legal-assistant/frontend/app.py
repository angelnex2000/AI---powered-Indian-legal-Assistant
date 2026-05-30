import os

import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="AI Legal Assistant", page_icon=":material/gavel:", layout="wide")

st.title("AI-Powered Indian Legal Assistant")
st.warning("This app gives general legal information, not professional legal advice. Consult a lawyer.")

with st.sidebar:
    st.header("Legal Sources")
    uploaded_file = st.file_uploader("Upload legal PDF", type=["pdf"])
    topic = st.selectbox(
        "Or use a sample law topic",
        [
            "bail",
            "consumer_rights",
            "cyber_crime",
            "property_dispute",
            "rental_agreement",
            "legal_notice",
            "constitution_basics",
        ],
    )
    language = st.radio("Answer language", ["english", "hindi"], horizontal=True)

    if uploaded_file and st.button("Process PDF", type="primary"):
        with st.spinner("Reading and indexing PDF..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            response = requests.post(f"{API_URL}/upload", files=files, timeout=120)

        if response.ok:
            data = response.json()
            st.success(data["message"])
            st.caption(f"{data.get('pages', 0)} pages, {data.get('chunks', 0)} chunks")
        else:
            st.error(response.json().get("detail", "Upload failed."))

    if st.button("Use Selected Topic"):
        with st.spinner("Adding topic notes..."):
            response = requests.post(f"{API_URL}/topic", data={"topic": topic}, timeout=60)

        if response.ok:
            data = response.json()
            st.success(data["message"])
            st.caption(f"{data.get('chunks', 0)} chunks added")
        else:
            st.error(response.json().get("detail", "Could not add topic."))

st.subheader("Ask a Legal Question")
question = st.text_area(
    "Question",
    placeholder="Example: Explain this agreement in simple words",
    height=100,
)

if st.button("Ask", type="primary", disabled=not question.strip()):
    with st.spinner("Searching documents and preparing answer..."):
        response = requests.post(
            f"{API_URL}/ask",
            data={"query": question, "language": language},
            timeout=120,
        )

    if response.ok:
        data = response.json()
        st.markdown("### Simple Answer")
        st.write(data["answer"])

        st.markdown("### Sources")
        sources = data.get("sources", [])
        if not sources:
            st.caption("No sources found yet. Upload and process a PDF, or use a sample law topic first.")

        for source in sources:
            with st.expander(f"{source['document_name']} - page {source['page_number']}"):
                st.write(source["text"])

        st.info(data["disclaimer"])
    else:
        st.error(response.json().get("detail", "Could not answer the question."))
