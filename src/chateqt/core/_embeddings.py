"""Embedding generation module."""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def generate_embeddings(documents: list[Document], output_path: Path) -> None:
    """Retrieve embeddings for the documents and save them to a local file.

    Args:
        documents (list[Document]): list of Langchain documents.
        output_path (Path, optional): Path to save the embeddings.
    """
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        task_type="retrieval_document",
    )
    vectors = FAISS.from_documents(documents, embedding=embeddings)
    logger.info(f"Saving the embeddings to {output_path=}.")
    vectors.save_local(output_path)


if __name__ == "__main__":
    from chateqt.core._parser import Parser

    parser = Parser()

    data_path = Path(*Path(__file__).parts[:-4]) / "data"
    raw_data_folder_path = data_path / "raw"
    embeddings_folder_path = data_path / "embeddings"

    base_documents = parser.parse_documents(
        folder_path=raw_data_folder_path / "base",
    )
    generate_embeddings(
        documents=base_documents,
        output_path=embeddings_folder_path / "base",
    )

    companies_documents = parser.parse_documents(
        folder_path=raw_data_folder_path / "companies",
    )
    generate_embeddings(
        documents=companies_documents,
        output_path=embeddings_folder_path / "companies",
    )
