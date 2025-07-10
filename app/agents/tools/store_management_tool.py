"""This module define the functions to interact with the vectorstore.

Functions:
    delete_docs: Delete documents from the vectorstore by their UUIDs.
    load_docs: Load documents into the vectorstore.
    retrieve_docs: Retrieve documents from the vectorstore based on a query.
"""
import os
from uuid import uuid4

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_google_community import BigQueryVectorStore
from langchain_google_vertexai import VertexAIEmbeddings

embedding = VertexAIEmbeddings(
    model_name="gemini-embedding-001",
    project=os.getenv("GOOGLE_CLOUD_PROJECT")
)

vectorstore = BigQueryVectorStore(
    project_id=os.getenv("GOOGLE_CLOUD_PROJECT"),
    dataset_name=os.getenv("BG_DATASET_NAME"),
    table_name=os.getenv("BG_TABLE_NAME"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION"),
    api_key=os.getenv("GEMINI_API_KEY"),    
    embedding=embedding
)

def delete_docs(uuids: list[str]):
    """Delete documents from the vectorstore by their UUIDs.

    Args:
        uuids (List[str]): List of UUIDs to delete.
    """
    vectorstore.delete(ids=uuids)

def load_docs(documents: list[Document]):
    """Load documents into the vectorstore.

    Args:
        documents (List[Document]): List of documents to load.
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    metas = [{'uuid': str(uuid4()), 'len': len(chunk)} for chunk in chunks]
    embs = embedding.embed(chunks)
    vectorstore.add_texts_with_embeddings(chunks, embs=embs, metadatas=metas)

def retrieve_docs(query: str) -> list[Document]:
    """Retrieve documents from the vectorstore based on a query.

    Args:
        query (str): Query to search for.

    Returns:
        List[Document]: List of retrieved documents.
    """
    return vectorstore.similarity_search(query)