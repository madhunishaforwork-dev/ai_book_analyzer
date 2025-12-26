import PyPDF2
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_pdf(uploaded_file):
    """
    Extract text from a PDF file with page metadata.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        tuple: (List[Document], page_count)
    """
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        documents = []
        page_count = len(pdf_reader.pages)
        
        for i, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if page_text:
                # Create a Document object with metadata
                doc = Document(
                    page_content=page_text,
                    metadata={"page": i + 1, "source": uploaded_file.name}
                )
                documents.append(doc)
            
            if i % 10 == 0:
                logger.debug(f"Processed {i}/{page_count} pages")
                
        return documents, page_count
    except Exception as e:
        logger.error(f"Error reading PDF: {e}")
        st.error(f"Error reading PDF: {e}")
        return [], 0

def chunk_documents(documents, chunk_size=1000, chunk_overlap=150):
    """
    Split documents into smaller chunks while preserving metadata.
    
    Args:
        documents (List[Document]): List of LangChain Documents
        chunk_size (int): Character size of each chunk
        chunk_overlap (int): Overlap between chunks
        
    Returns:
        List[Document]: List of chunked documents
    """
    if not documents:
        return []
        
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        add_start_index=True,
    )
    
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Split {len(documents)} pages into {len(chunks)} chunks")
    return chunks
