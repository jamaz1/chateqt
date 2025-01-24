"""Embedding generation module."""

from dataclasses import dataclass
import logging
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


@dataclass
class MarkdownLoader:
    file_path: Path

    def load(self) -> list[Document]:
        with open(self.file_path) as f:
            text = f.read()
        return [Document(page_content=text)]


class Parser:
    def __init__(
        self,
        chunk_size: int = 5000,  # larger than unnecessary, but time for tuning is limited.  # noqa: E501
        chunk_overlap: int = 500,
    ) -> None:
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def _get_loader(self, file_path: Path) -> PyPDFLoader | MarkdownLoader:
        ext = file_path.suffix.lower()
        if ext == ".pdf":
            return PyPDFLoader(file_path)

        return MarkdownLoader(file_path)

    def _merge_short_documents(
        self,
        documents: list[Document],
        min_length: int = 500,
    ) -> list[Document]:
        final_docs = []
        page_content_buffer = ""

        for doc in documents:
            page_content_buffer += "\n" + doc.page_content
            if len(doc.page_content) < min_length:
                continue

            final_docs.append(
                Document(
                    metadata=doc.metadata,
                    page_content=page_content_buffer.strip(),
                ),
            )
            page_content_buffer = ""

        return [i for i in final_docs if len(i.page_content) > min_length]

    def parse_documents(
        self,
        folder_path: str,
    ) -> list[Document]:
        """Load documents from the given folder path and parse into chunks.

        Args:
            folder_path (str): Path to the folder containing the input data files.
            chunk_size (int, optional): Size of the chunks to split the documents into.
            chunk_overlap (int, optional): Overlap between the chunks.

        Returns:
            list[Document]: List of Langchain documents.
        """
        documents = []
        files_paths = list(Path(folder_path).glob("**/*"))
        for doc_path in files_paths:
            logger.info(f"Processing {doc_path}")

            loader = self._get_loader(doc_path)

            logger.debug(f"Loading {doc_path}")
            docs = loader.load()
            docs = self._merge_short_documents(docs)

            logger.debug(f"Splitting {doc_path} into chunks")
            chunks = self.text_splitter.split_documents(docs)
            logger.debug(f"Split {doc_path} into {len(chunks)} chunks")

            documents.extend(chunks)

        logger.info(f"Parsed {len(files_paths)} files into {len(documents)} documents.")
        return documents


if __name__ == "__main__":
    ROOT = Path(*Path(__file__).parts[:-4])
    RAW_DATA_FODLER_PATH = ROOT / "data" / "raw"
    VECTOR_STORE_PATH = ROOT / "data" / "faiss_index"

    parser = Parser()
    documents = parser.parse_documents(folder_path=RAW_DATA_FODLER_PATH)
