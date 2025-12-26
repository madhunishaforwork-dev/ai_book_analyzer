
import os
import pickle
import numpy as np
import streamlit as st
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
CACHE_DIR = "./.cache/models"

class SemanticSearchEngine:
    """
    Handles semantic embeddings and vector retrieval for the book content.
    Uses 'all-MiniLM-L6-v2' (Sentencetransformers) and FAISS.
    """
    
    def __init__(self):
        self._check_cache()
        try:
            # Initialize embeddings - cached to avoid re-downloading
            self.embeddings = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL_NAME,
                cache_folder=CACHE_DIR
            )
            logger.info(f"Loaded embedding model: {EMBEDDING_MODEL_NAME}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.embeddings = None
            
        self.vector_store = None

    def _check_cache(self):
        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR, exist_ok=True)

    def build_index(self, chunks):
        """
        Builds the FAISS vector index from document chunks.
        
        Args:
            chunks (List[Document]): List of LangChain Document objects
        """
        if not chunks or not self.embeddings:
            logger.warning("No chunks or embedding model unavailable.")
            return False

        try:
            with st.spinner(f"Indexing {len(chunks)} semantic vectors..."):
                self.vector_store = FAISS.from_documents(chunks, self.embeddings)
                logger.info("Vector store built successfully.")
                return True
        except Exception as e:
            logger.error(f"Error building vector store: {e}")
            st.error(f"Failed to build semantic index: {e}")
            return False

    def search(self, query, k=4):
        """
        Semantic search for the query.
        
        Args:
            query (str): User question/query
            k (int): Number of results to return
            
        Returns:
            List[Document]: Top k most relevant chunks with metadata
        """
        if not self.vector_store:
            return []
            
        try:
            # Performs cosine similarity search
            results = self.vector_store.similarity_search(query, k=k)
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def get_related_concepts(self, query, k=10):
        """
        Finds broadly related content for concept mapping (wider search).
        """
        return self.search(query, k=k)
