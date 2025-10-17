"""
SafetyAgent AI - Main FastAPI Application
AI-powered safety knowledge base with document processing and chat interface
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
from pathlib import Path

# FastAPI imports
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# Document loader
from document_loader import SafetyAgentDocumentLoader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SafetyAgent AI",
    description="AI-powered safety knowledge base and chat system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global document loader instance
document_loader: Optional[SafetyAgentDocumentLoader] = None

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    session_id: str
    timestamp: str
    confidence: float

class DocumentUploadResponse(BaseModel):
    message: str
    doc_id: str
    filename: str
    chunks_count: int
    file_size: int

class SystemStats(BaseModel):
    total_documents: int
    total_chunks: int
    file_types: Dict[str, int]
    vector_store_path: str
    chunk_size: int
    chunk_overlap: int

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    documents_loaded: bool

# Dependency to get document loader
def get_document_loader() -> SafetyAgentDocumentLoader:
    global document_loader
    if document_loader is None:
        raise HTTPException(status_code=503, detail="Document loader not initialized")
    return document_loader

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove broken connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

# API Routes

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the main frontend page"""
    try:
        frontend_path = Path(__file__).parent.parent / "frontend" / "index.html"
        if frontend_path.exists():
            return HTMLResponse(content=frontend_path.read_text())
        else:
            return HTMLResponse(content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>SafetyAgent AI</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .status { padding: 20px; background: #f0f8ff; border-radius: 8px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🛡️ SafetyAgent AI</h1>
                    <div class="status">
                        <h2>System Status</h2>
                        <p>✅ Backend API is running</p>
                        <p>📚 Document processing ready</p>
                        <p>💬 Chat interface available</p>
                        <p><a href="/api/docs">View API Documentation</a></p>
                    </div>
                </div>
            </body>
            </html>
            """)
    except Exception as e:
        logger.error(f"Error serving frontend: {e}")
        return HTMLResponse(content="<h1>SafetyAgent AI</h1><p>Frontend not available</p>")

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(message: ChatMessage, loader: SafetyAgentDocumentLoader = Depends(get_document_loader)):
    """Chat endpoint for AI conversations"""
    try:
        # Create QA chain
        qa_chain = loader.create_qa_chain()
        
        # Get answer with sources
        result = qa_chain({"query": message.message})
        
        # Extract sources
        sources = []
        for doc in result.get("source_documents", []):
            source = {
                "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                "source_file": doc.metadata.get("file_name", "Unknown"),
                "doc_id": doc.metadata.get("doc_id", "Unknown"),
                "page": doc.metadata.get("page", 0)
            }
            sources.append(source)
        
        # Calculate confidence based on source relevance
        confidence = min(len(sources) / 5.0, 1.0) if sources else 0.0
        
        response = ChatResponse(
            answer=result["result"],
            sources=sources,
            session_id=message.session_id or f"session_{datetime.now().timestamp()}",
            timestamp=datetime.now().isoformat(),
            confidence=confidence
        )
        
        logger.info(f"Chat response generated for query: {message.message[:50]}...")
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket)
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            
            # Parse message (simple JSON for now)
            import json
            try:
                message_data = json.loads(data)
                query = message_data.get("message", "")
            except:
                query = data
            
            if not query:
                continue
            
            # Get document loader
            loader = get_document_loader()
            
            # Create QA chain
            qa_chain = loader.create_qa_chain()
            
            # Get answer
            result = qa_chain({"query": query})
            
            # Send response
            response = {
                "answer": result["result"],
                "sources": [
                    {
                        "source_file": doc.metadata.get("file_name", "Unknown"),
                        "content": doc.page_content[:100] + "..."
                    }
                    for doc in result.get("source_documents", [])[:3]
                ],
                "timestamp": datetime.now().isoformat()
            }
            
            await manager.send_personal_message(json.dumps(response), websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@app.post("/api/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    category: str = "general",
    loader: SafetyAgentDocumentLoader = Depends(get_document_loader)
):
    """Upload and process a document"""
    try:
        # Validate file type
        allowed_extensions = ['.docx', '.doc', '.pdf', '.txt', '.md']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not supported. Allowed: {allowed_extensions}"
            )
        
        # Save uploaded file
        upload_dir = Path("data/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process document
        metadata = {
            "category": category,
            "uploaded_at": datetime.now().isoformat(),
            "original_filename": file.filename
        }
        
        doc_id = loader.load_document(str(file_path), metadata)
        
        # Get document info
        doc_info = loader.documents_metadata.get(doc_id, {})
        chunks_count = doc_info.get("chunks_count", 0)
        
        response = DocumentUploadResponse(
            message="Document uploaded and processed successfully",
            doc_id=doc_id,
            filename=file.filename,
            chunks_count=chunks_count,
            file_size=len(content)
        )
        
        logger.info(f"Document uploaded: {file.filename} (ID: {doc_id})")
        return response
        
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents")
async def list_documents(loader: SafetyAgentDocumentLoader = Depends(get_document_loader)):
    """List all documents in the knowledge base"""
    try:
        documents = []
        for doc_id, meta in loader.documents_metadata.items():
            documents.append({
                "id": doc_id,
                "filename": meta["metadata"].get("file_name", "Unknown"),
                "category": meta["metadata"].get("category", "general"),
                "chunks_count": meta["chunks_count"],
                "loaded_at": meta["loaded_at"],
                "file_size": os.path.getsize(meta["file_path"]) if os.path.exists(meta["file_path"]) else 0
            })
        
        return {"documents": documents}
        
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: str, loader: SafetyAgentDocumentLoader = Depends(get_document_loader)):
    """Delete a document from the knowledge base"""
    try:
        success = loader.delete_document(doc_id)
        if success:
            return {"message": f"Document {doc_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
            
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reindex")
async def reindex_documents(loader: SafetyAgentDocumentLoader = Depends(get_document_loader)):
    """Reindex all documents in the knowledge base"""
    try:
        success = loader.reindex_documents()
        if success:
            return {"message": "Documents reindexed successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to reindex documents")
            
    except Exception as e:
        logger.error(f"Error reindexing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search")
async def search_documents(
    query: str,
    k: int = 5,
    loader: SafetyAgentDocumentLoader = Depends(get_document_loader)
):
    """Search documents in the knowledge base"""
    try:
        sources = loader.get_document_sources(query, k)
        return {
            "query": query,
            "results": sources,
            "total_results": len(sources)
        }
        
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats", response_model=SystemStats)
async def get_system_stats(loader: SafetyAgentDocumentLoader = Depends(get_document_loader)):
    """Get system statistics"""
    try:
        stats = loader.get_stats()
        return SystemStats(**stats)
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    global document_loader
    
    documents_loaded = document_loader is not None and len(document_loader.documents_metadata) > 0
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        documents_loaded=documents_loaded
    )

# Mount static files
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the document loader on startup"""
    global document_loader
    
    logger.info("Starting SafetyAgent AI...")
    
    try:
        # Initialize document loader
        document_loader = SafetyAgentDocumentLoader(
            persist_directory="./data/chroma_db",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Try to load the safety manual if it exists
        safety_manual_path = "../EmployeeSafetyManual.docx"
        if os.path.exists(safety_manual_path):
            try:
                doc_id = document_loader.load_document(
                    safety_manual_path,
                    {"category": "safety_manual", "name": "Employee Safety Manual"}
                )
                logger.info(f"Loaded safety manual: {doc_id}")
            except Exception as e:
                logger.error(f"Error loading safety manual: {e}")
        
        logger.info("SafetyAgent AI initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing SafetyAgent AI: {e}")
        raise

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down SafetyAgent AI...")

if __name__ == "__main__":
    # Create data directory
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/uploads", exist_ok=True)
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
