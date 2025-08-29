from typing import List

from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings

persist_directory = ".chroma_db"  # setting


def create_chroma(embeddings: Embeddings, texts: List[str], metadatas: List[dict], collection_name: str) -> Chroma:
    return Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas,
        collection_name=collection_name,
        persist_directory=persist_directory
    )


def get_chroma(embedding_function: Embeddings, collection_name: str) -> Chroma:
    return Chroma(
        embedding_function=embedding_function,
        collection_name=collection_name,
        persist_directory=persist_directory
    )
