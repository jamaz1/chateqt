"""Query module."""

import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
import google.generativeai as genai
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
import streamlit as st
from streamlit_chat import message

from chateqt.core import TEMPLATE

load_dotenv()
logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


class ChatbotEQT:
    def __init__(self, vector_stores_path: str) -> None:
        self.__load_embedding_model()
        self.__load_vector_stores(vector_stores_path)
        self.__load_chain()

    def __load_embedding_model(self) -> None:
        logger.info("Loading the embedding model.")
        self._embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            task_type="retrieval_query",
        )

    def __load_vector_stores(self, vector_stores_path: Path) -> None:
        logger.info("Loading the vector store.")
        self._base_vector_store = FAISS.load_local(
            folder_path=vector_stores_path / "base",
            embeddings=self._embeddings,
            allow_dangerous_deserialization=True,
        )
        self._companies_vector_store = FAISS.load_local(
            folder_path=vector_stores_path / "companies",
            embeddings=self._embeddings,
            allow_dangerous_deserialization=True,
        )

    def __load_chain(self) -> None:
        logger.info("Loading the chain.")
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0)
        prompt = ChatPromptTemplate.from_template(template=TEMPLATE)
        self._chain = create_stuff_documents_chain(llm=llm, prompt=prompt)

    def get_relevant_documents(
        self,
        user_question: str,
        n_documents: int = 10,
    ) -> list[Document]:
        logger.info("Searching for relevant documents from the index report.")
        base_docs = self._base_vector_store.similarity_search(
            query=user_question,
            k=n_documents,
        )

        logger.info("Searching for relevant documents from the companies data.")
        companies_docs = self._companies_vector_store.similarity_search(
            query=user_question,
            k=n_documents,
        )

        docs = base_docs + companies_docs

        # This is not ideal and can be improved by tracking the original
        # source of the document using the metadata of the Document instead
        # of having the llm deduct the source.
        new_docs = []
        for doc in docs:
            page_content = (
                "page-number " + doc.metadata["page_label"] + ": " + doc.page_content
                if doc.metadata.get("page_label") is not None
                else doc.page_content
            )

            new_docs.append(
                Document(id=doc.id, metadata=doc.metadata, page_content=page_content),
            )
        return new_docs

    def call_llm(
        self,
        user_input: str,
        relevant_docs: list[Document],
    ) -> Any:  # noqa: ANN401
        logger.info("Retrieving an answer for the question.")
        return self._chain.invoke(
            {
                "context": relevant_docs,
                "question": user_input,
            },
        )


if __name__ == "__main__":
    vector_store_path = Path(*Path(__file__).parts[:-4]) / "data" / "embeddings"
    bot = ChatbotEQT(vector_stores_path=vector_store_path)
    # st.set_page_config(layout="wide")

    st.title("ChatEQT 💬")
    st.subheader(
        "Ask me about how AI impacts the different companies in the EQT X fund.",
    )
    # user_question = st.chat_input(placeholder="Type your question here...")
    if user_question := st.chat_input("Type your question here..."):
        message(user_question, avatar_style="no-avatar", is_user=True)

    if user_question and len(user_question) > 0:
        relevant_docs = bot.get_relevant_documents(user_question=user_question)
        response = bot.call_llm(user_input=user_question, relevant_docs=relevant_docs)

        message(response, avatar_style="no-avatar")
