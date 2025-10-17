# SafetyAgent AI - Intelligent Safety Knowledge Base

🛡️ **SafetyAgent AI** is a sophisticated AI-powered safety knowledge base system that allows employees to interact with an intelligent assistant that can reference and answer questions from company safety manuals and documents.

## 🚀 Features

### 🤖 AI-Powered Knowledge Base
- **Document Processing**: Upload and process Word documents (.docx), PDFs, and text files
- **Intelligent Chunking**: Advanced text splitting with LangChain for optimal retrieval
- **Vector Search**: Semantic search using OpenAI embeddings and ChromaDB
- **Context-Aware Responses**: Answers grounded in your actual safety documents

### 💬 Modern Chat Interface
- **Floating Chat Widget**: Fixed bottom-left chat icon for easy access
- **Real-time Communication**: WebSocket support for streaming responses
- **Source Citations**: Every answer includes references to source documents
- **Confidence Scoring**: Know how confident the AI is in its responses

### 📚 Document Management
- **Easy Upload**: Drag-and-drop or browse to upload documents
- **Multiple Formats**: Support for .docx, .doc, .pdf, .txt, .md files
- **Automatic Processing**: Documents are automatically chunked and indexed
- **Reindexing**: Update the knowledge base when documents change

### 🔍 Advanced Search
- **Semantic Search**: Find relevant information even with different wording
- **Multi-Document Search**: Search across all uploaded safety documents
- **Similarity Scoring**: Results ranked by relevance
- **Context Retrieval**: Get the most relevant sections for your questions

## 🏗️ Architecture

### Backend Stack
- **FastAPI**: Modern, fast web framework for building APIs
- **LangChain**: Framework for developing applications with LLMs
- **ChromaDB**: Vector database for storing and searching embeddings
- **OpenAI**: GPT models for generating intelligent responses
- **WebSocket**: Real-time communication for streaming responses

### Frontend Stack
- **Vanilla JavaScript**: Modern ES6+ with clean, maintainable code
- **CSS3**: Responsive design with modern styling and animations
- **WebSocket Client**: Real-time chat interface
- **Progressive Enhancement**: Works without JavaScript for basic functionality

## 📋 Prerequisites

- Python 3.11+
- OpenAI API key
- Docker (optional, for containerized deployment)

## 🚀 Quick Start

### Option 1: Local Development

1. **Clone and Setup**
   ```bash
   cd safety-agent-v2
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   cp env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Start the Application**
   ```bash
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Access the Application**
   - Open your browser to `http://localhost:8000`
   - Click the chat icon in the bottom-left corner
   - Upload your safety documents and start asking questions!

### Option 2: Docker Deployment

1. **Environment Setup**
   ```bash
   export OPENAI_API_KEY="your_openai_api_key_here"
   ```

2. **Build and Run**
   ```bash
   docker-compose up --build
   ```

3. **Access the Application**
   - Open your browser to `http://localhost:8000`

## 📖 Usage Guide

### 1. Upload Documents
- Click the "Upload Document" button in the header
- Drag and drop your safety documents or browse to select them
- Choose a category (Safety Manual, Procedures, Regulations, etc.)
- Documents are automatically processed and indexed

### 2. Chat with SafetyAgent
- Click the chat icon in the bottom-left corner
- Ask questions about your safety procedures
- Get instant, accurate answers with source citations
- Use suggestion buttons for common queries

### 3. Example Queries
- "What are the general safety requirements for employees?"
- "What PPE is required for chemical handling?"
- "How do I report a safety incident?"
- "What should I do in case of an emergency?"

### 4. Document Management
- View uploaded documents in the upload modal
- Delete documents if needed
- Check system statistics to see document counts and types

## 🔧 API Documentation

The application includes comprehensive API documentation:

- **Swagger UI**: `http://localhost:8000/api/docs`
- **ReDoc**: `http://localhost:8000/api/redoc`

### Key Endpoints

- `POST /api/chat` - Chat with the AI assistant
- `POST /api/upload` - Upload and process documents
- `GET /api/documents` - List all documents
- `GET /api/search` - Search documents
- `GET /api/stats` - Get system statistics
- `WebSocket /ws/chat` - Real-time chat interface

## 🐳 Docker Configuration

### Development
```bash
docker-compose up --build
```

### Production
```bash
docker-compose --profile production up -d
```

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `DEBUG`: Enable debug mode (default: True)
- `CHROMA_PERSIST_DIRECTORY`: Vector database storage path

## 📁 Project Structure

```
safety-agent-v2/
├── backend/
│   ├── main.py              # FastAPI application
│   └── document_loader.py   # Document processing and vector storage
├── frontend/
│   ├── index.html           # Main application interface
│   ├── styles.css           # Modern CSS styling
│   └── app.js              # Frontend application logic
├── data/                    # Data storage (created automatically)
│   ├── chroma_db/          # Vector database
│   └── uploads/            # Uploaded files
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
├── env.example             # Environment variables template
└── README.md               # This file
```

## 🔒 Security Considerations

- **API Key Protection**: Store OpenAI API keys securely
- **File Upload Validation**: Only allow specific file types
- **CORS Configuration**: Configure allowed origins for production
- **Input Sanitization**: All user inputs are sanitized
- **Rate Limiting**: Consider implementing rate limiting for production

## 🚀 Production Deployment

### Environment Setup
1. Set up a production environment with proper security
2. Configure environment variables
3. Set up SSL/TLS certificates
4. Configure reverse proxy (nginx)
5. Set up monitoring and logging

### Scaling Considerations
- Use a production-grade database for metadata
- Implement caching for frequently accessed data
- Consider load balancing for multiple instances
- Set up proper backup strategies for the vector database

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the API documentation at `/api/docs`
- Review the logs for error messages
- Ensure your OpenAI API key is valid and has sufficient credits
- Verify that uploaded documents are in supported formats

## 🔮 Future Enhancements

- **Authentication**: Company email-based authentication
- **Analytics**: Query analytics and usage tracking
- **Multi-language Support**: Support for multiple languages
- **Advanced Search**: Filters, date ranges, and advanced query options
- **Document Versioning**: Track document changes and versions
- **Integration**: API integrations with existing safety management systems

---

**SafetyAgent AI** - Making safety information accessible and intelligent! 🛡️
