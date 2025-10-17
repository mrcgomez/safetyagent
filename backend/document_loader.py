"""
Document Loader for SafetyAgent AI
Handles Word document processing, chunking, and vector storage using LangChain and ChromaDB
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib
from datetime import datetime

# LangChain imports
from langchain.document_loaders import (
    Docx2txtLoader,
    TextLoader,
    PyPDFLoader,
    UnstructuredMarkdownLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

# ChromaDB
import chromadb
from chromadb.config import Settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SafetyAgentDocumentLoader:
    """
    Document loader and vector store manager for SafetyAgent AI
    """
    
    def __init__(self, 
                 persist_directory: str = "./data/chroma_db",
                 openai_api_key: Optional[str] = None,
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200):
        
        self.persist_directory = persist_directory
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=openai_api_key or os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Initialize vector store
        self.vectorstore = None
        self._initialize_vectorstore()
        
        # Document metadata
        self.documents_metadata = {}
        
        logger.info("SafetyAgent Document Loader initialized")
    
    def _initialize_vectorstore(self):
        """Initialize ChromaDB vector store"""
        try:
            # Ensure directory exists
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # Initialize ChromaDB
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name="safety_documents"
            )
            
            logger.info(f"Vector store initialized at {self.persist_directory}")
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            raise
    
    def load_document(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Load and process a document into the vector store
        
        Args:
            file_path: Path to the document file
            metadata: Optional metadata for the document
            
        Returns:
            Document ID
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"Document not found: {file_path}")
            
            # Generate document ID
            doc_id = self._generate_doc_id(file_path)
            
            # Load document based on file type
            documents = self._load_document_by_type(file_path)
            
            if not documents:
                raise ValueError(f"No content extracted from {file_path}")
            
            # Add metadata to documents
            doc_metadata = {
                "source": str(file_path),
                "doc_id": doc_id,
                "file_name": file_path.name,
                "file_type": file_path.suffix.lower(),
                "loaded_at": datetime.now().isoformat(),
                **(metadata or {})
            }
            
            for doc in documents:
                doc.metadata.update(doc_metadata)
            
            # Split documents into chunks
            chunks = self.text_splitter.split_documents(documents)
            
            logger.info(f"Split document into {len(chunks)} chunks")
            
            # Add to vector store
            self.vectorstore.add_documents(chunks)
            
            # Persist the vector store
            self.vectorstore.persist()
            
            # Store document metadata
            self.documents_metadata[doc_id] = {
                "file_path": str(file_path),
                "chunks_count": len(chunks),
                "metadata": doc_metadata,
                "loaded_at": datetime.now().isoformat()
            }
            
            logger.info(f"Successfully loaded document: {file_path.name} (ID: {doc_id})")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {e}")
            raise
    
    def _load_document_by_type(self, file_path: Path) -> List[Document]:
        """Load document based on file type"""
        file_ext = file_path.suffix.lower()
        
        try:
            if file_ext in ['.docx', '.doc']:
                loader = Docx2txtLoader(str(file_path))
            elif file_ext == '.pdf':
                loader = PyPDFLoader(str(file_path))
            elif file_ext == '.md':
                loader = UnstructuredMarkdownLoader(str(file_path))
            elif file_ext in ['.txt']:
                loader = TextLoader(str(file_path), encoding='utf-8')
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} pages/sections from {file_path.name}")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            raise
    
    def _generate_doc_id(self, file_path: Path) -> str:
        """Generate unique document ID"""
        # Use file path and modification time for uniqueness
        file_info = f"{file_path}_{file_path.stat().st_mtime}"
        file_hash = hashlib.md5(file_info.encode()).hexdigest()[:12]
        return f"doc_{file_hash}"
    
    def search_documents(self, query: str, k: int = 5, filter_metadata: Optional[Dict] = None) -> List[Document]:
        """
        Search for relevant documents
        
        Args:
            query: Search query
            k: Number of results to return
            filter_metadata: Optional metadata filter
            
        Returns:
            List of relevant documents
        """
        try:
            if not self.vectorstore:
                raise ValueError("Vector store not initialized")
            
            # Perform similarity search
            docs = self.vectorstore.similarity_search(
                query=query,
                k=k,
                filter=filter_metadata
            )
            
            logger.info(f"Found {len(docs)} relevant documents for query: {query[:50]}...")
            return docs
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def get_document_sources(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Get document sources with similarity scores
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of sources with metadata and scores
        """
        try:
            if not self.vectorstore:
                raise ValueError("Vector store not initialized")
            
            # Perform similarity search with scores
            docs_with_scores = self.vectorstore.similarity_search_with_score(
                query=query,
                k=k
            )
            
            sources = []
            for doc, score in docs_with_scores:
                source = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": float(score),
                    "source_file": doc.metadata.get("file_name", "Unknown"),
                    "doc_id": doc.metadata.get("doc_id", "Unknown")
                }
                sources.append(source)
            
            return sources
            
        except Exception as e:
            logger.error(f"Error getting document sources: {e}")
            return []
    
    def create_qa_chain(self, llm_model: str = "gpt-3.5-turbo") -> RetrievalQA:
        """
        Create a question-answering chain
        
        Args:
            llm_model: LLM model to use
            
        Returns:
            RetrievalQA chain
        """
        try:
            if not self.vectorstore:
                raise ValueError("Vector store not initialized")
            
            # Initialize LLM
            llm = ChatOpenAI(
                model_name=llm_model,
                temperature=0.1,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
            
            # Create retrieval QA chain
            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=self.vectorstore.as_retriever(
                    search_kwargs={"k": 5}
                ),
                return_source_documents=True
            )
            
            logger.info(f"Created QA chain with model: {llm_model}")
            return qa_chain
            
        except Exception as e:
            logger.error(f"Error creating QA chain: {e}")
            raise
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document from the vector store
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if doc_id not in self.documents_metadata:
                logger.warning(f"Document {doc_id} not found in metadata")
                return False
            
            # Note: ChromaDB doesn't have a direct delete by metadata method
            # This would require rebuilding the vector store without the document
            # For now, we'll just remove from metadata
            del self.documents_metadata[doc_id]
            
            logger.info(f"Removed document {doc_id} from metadata")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the document loader"""
        try:
            total_docs = len(self.documents_metadata)
            total_chunks = sum(
                meta["chunks_count"] 
                for meta in self.documents_metadata.values()
            )
            
            file_types = {}
            for meta in self.documents_metadata.values():
                file_type = meta["metadata"].get("file_type", "unknown")
                file_types[file_type] = file_types.get(file_type, 0) + 1
            
            return {
                "total_documents": total_docs,
                "total_chunks": total_chunks,
                "file_types": file_types,
                "vector_store_path": self.persist_directory,
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def reindex_documents(self) -> bool:
        """
        Reindex all documents in the vector store
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Starting document reindexing...")
            
            # Clear existing vector store
            if os.path.exists(self.persist_directory):
                import shutil
                shutil.rmtree(self.persist_directory)
            
            # Reinitialize vector store
            self._initialize_vectorstore()
            
            # Reload all documents
            for doc_id, meta in self.documents_metadata.items():
                file_path = meta["file_path"]
                if os.path.exists(file_path):
                    self.load_document(file_path, meta["metadata"])
            
            logger.info("Document reindexing completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error reindexing documents: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Initialize document loader
    loader = SafetyAgentDocumentLoader()
    
    # Load a document
    doc_path = "../EmployeeSafetyManual.docx"
    if os.path.exists(doc_path):
        doc_id = loader.load_document(doc_path, {"category": "safety_manual"})
        print(f"Loaded document with ID: {doc_id}")
        
        # Test search
        results = loader.search_documents("What are the safety requirements?", k=3)
        print(f"Found {len(results)} relevant documents")
        
        # Get stats
        stats = loader.get_stats()
        print(f"Stats: {stats}")
    else:
        print(f"Document not found: {doc_path}")
