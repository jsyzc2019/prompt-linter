from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain import OpenAI, Cohere
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.embeddings import CohereEmbeddings, OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.docstore.document import Document
from langchain.vectorstores import FAISS, VectorStore
import docx2txt
import requests
from readability import Document as ReadabilityDocument
from typing import List, Dict, Any
import re
from io import BytesIO
import streamlit as st
from prompts import STUFF_PROMPT
from pypdf import PdfReader
from openai.error import AuthenticationError


@st.experimental_memo()
def parse_docx(file: BytesIO) -> str:
    text = docx2txt.process(file)
    # Remove multiple newlines
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text


@st.experimental_memo()
def parse_pdf(file: BytesIO) -> List[str]:
    pdf = PdfReader(file)
    output = []
    for page in pdf.pages:
        text = page.extract_text()
        # Merge hyphenated words
        text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
        # Fix newlines in the middle of sentences
        text = re.sub(r"(?<!\n\s)\n(?!\s\n)", " ", text.strip())
        # Remove multiple newlines
        text = re.sub(r"\n\s*\n", "\n\n", text)

        output.append(text)

    return output


@st.experimental_memo()
def parse_txt(file: BytesIO) -> str:
    text = file.read().decode("utf-8")
    # Remove multiple newlines
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text


@st.cache(allow_output_mutation=True)
def text_to_docs(text: str | List[str]) -> List[Document]:
    """Converts a string or list of strings to a list of Documents
    with metadata."""
    if isinstance(text, str):
        # Take a single string as one page
        text = [text]
    page_docs = [Document(page_content=page) for page in text]

    # Add page numbers as metadata
    for i, doc in enumerate(page_docs):
        doc.metadata["page"] = i + 1

    # Split pages into chunks
    doc_chunks = []

    for doc in page_docs:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
            chunk_overlap=0,
        )
        chunks = text_splitter.split_text(doc.page_content)
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk, metadata={"page": doc.metadata["page"], "chunk": i}
            )
            # Add sources a metadata
            doc.metadata["source"] = f"{doc.metadata['page']}-{doc.metadata['chunk']}"
            doc_chunks.append(doc)
    return doc_chunks


@st.cache(allow_output_mutation=True)
def embed_docs(docs: List[Document]) -> VectorStore:
    """Embeds a list of Documents and returns a FAISS index"""

    if not st.session_state.get("OPENAI_API_KEY"):
        raise AuthenticationError(
            "Enter your OpenAI API key in the sidebar. You can get a key at https://platform.openai.com/account/api-keys."
        )
    else:
        # Embed the chunks
        embeddings = OpenAIEmbeddings(openai_api_key=st.session_state.get("OPENAI_API_KEY"))  # type: ignore
        index = FAISS.from_documents(docs, embeddings)

        return index


@st.cache(allow_output_mutation=True)
def search_docs(index: VectorStore, query: str) -> List[Document]:
    """Searches a FAISS index for similar chunks to the query
    and returns a list of Documents."""

    # Search for similar chunks
    docs = index.similarity_search(query, k=5)
    return docs


@st.cache(allow_output_mutation=True)
def get_answer(docs: List[Document], query: str) -> Dict[str, Any]:
    """Gets an answer to a question from a list of Documents."""

    # Get the answer

    chain = load_qa_with_sources_chain(OpenAI(temperature=0, openai_api_key=st.session_state.get("OPENAI_API_KEY")), chain_type="stuff", prompt=STUFF_PROMPT)  # type: ignore

    # Cohere doesn't work very well as of now.
    # chain = load_qa_with_sources_chain(Cohere(temperature=0), chain_type="stuff", prompt=STUFF_PROMPT)  # type: ignore
    answer = chain(
        {"input_documents": docs, "question": query}, return_only_outputs=True
    )
    return answer


@st.cache(allow_output_mutation=True)
def get_sources(answer: Dict[str, Any], docs: List[Document]) -> List[Document]:
    """Gets the source documents for an answer."""

    # Get sources for the answer
    source_keys = [s for s in answer["output_text"].split("SOURCES: ")[-1].split(", ")]

    source_docs = []
    for doc in docs:
        if doc.metadata["source"] in source_keys:
            source_docs.append(doc)

    return source_docs


def wrap_text_in_html(text: str | List[str]) -> str:
    """Wraps each text block separated by newlines in <p> tags"""
    if isinstance(text, list):
        # Add horizontal rules between pages
        text = "\n<hr/>\n".join(text)
    return "".join([f"<p>{line}</p>" for line in text.split("\n")])

@st.experimental_memo()
def parse_url(url: str) -> str:
    """Parses a URL and returns the text content"""
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        doc = ReadabilityDocument(response.text)
        text = doc.summary(html_partial=True)
        text = re.sub(r"<[^>]*>", "", text)
        # Stripe multiple newlines, big spaces, and tabs
        text = re.sub(r"\n\s*\n", "\n\n", text)
        text = re.sub(r"\s{3,}", " ", text)
        # text = re.sub(r"\t", "", text)
        return text
    except requests.exceptions.HTTPError as error:
        st.error(f"Error on fetch page: {error}")
        return ""