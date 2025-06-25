# Enhanced RAG - Production Deployment

A production-grade RAG (Retrieval-Augmented Generation) application for prompt engineering, featuring advanced search capabilities and modern web interfaces.

## 🚀 Live Demo

- **GitHub Pages**: [https://your-username.github.io/enhanced-rag](https://your-username.github.io/enhanced-rag)
- **API Documentation**: [https://your-username.github.io/enhanced-rag/api-docs.html](https://your-username.github.io/enhanced-rag/api-docs.html)

## ✨ Features

### 🧠 **Smart Categorization**

- Gemini API integration for intelligent prompt technique identification
- Automatic categorization of user prompts based on "The Prompt Report" taxonomy

### 🔍 **Advanced Search**

- **Hybrid Search**: Combines FAISS vector search with BM25 keyword search
- **Multiple Strategies**: Vector-only, keyword-only, or hybrid approaches
- **Semantic Embeddings**: Using sentence-transformers for high-quality embeddings

### 📚 **Comprehensive Knowledge Base**

- Complete database of prompt engineering techniques from "The Prompt Report"
- Advanced document chunking with multiple strategies
- Persistent vector storage with FAISS

### ✨ **AI Enhancement**

- TinyLlama integration via Ollama for local prompt enhancement
- Context-aware improvements based on identified techniques

### 🌐 **Multiple Interfaces**

- **Streamlit**: Interactive web application
- **FastAPI**: RESTful API with OpenAPI documentation
- **Static HTML**: GitHub Pages compatible interface

## 🏗️ Architecture

```
User Prompt → Gemini API → FAISS Vector DB → TinyLlama → Enhanced Prompt
              (Categorize)   (Retrieve)      (Enhance)
```

### Technologies Used

- **Backend**: FastAPI, Python 3.11+
- **AI/ML**: Gemini API, FAISS, sentence-transformers, Ollama/TinyLlama
- **Frontend**: Streamlit, HTML/CSS/JavaScript
- **Search**: Hybrid approach (FAISS + BM25)
- **Deployment**: Docker, GitHub Actions, GitHub Pages
- **Testing**: pytest, comprehensive test suite

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Gemini API key
- Ollama (for local enhancement)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/enhanced-rag.git
   cd enhanced-rag
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**

   ```bash
   export GEMINI_API_KEY="your-gemini-api-key"
   ```

4. **Install and run Ollama (for local enhancement)**
   ```bash
   # Install Ollama (see https://ollama.ai/)
   ollama pull tinyllama
   ollama serve
   ```

### Running the Application

#### Option 1: FastAPI + Static Interface

```bash
python api.py
# Visit http://localhost:8000
```

#### Option 2: Streamlit Interface

```bash
streamlit run streamlit_app.py
# Visit http://localhost:8501
```

#### Option 3: Docker Compose

```bash
docker-compose up
# API: http://localhost:8000
# Streamlit: http://localhost:8501
```

## 📖 API Documentation

### Endpoints

- `GET /api/health` - Health check
- `POST /api/enhance-prompt` - Enhance user prompts
- `POST /api/search` - Search knowledge base
- `GET /api/techniques` - List all techniques
- `GET /api/techniques/{name}` - Get technique details

### Example Usage

```python
import requests

# Enhance a prompt
response = requests.post("http://localhost:8000/api/enhance-prompt", json={
    "prompt": "Help me write a professional email"
})

# Search knowledge base
response = requests.post("http://localhost:8000/api/search", json={
    "query": "few shot examples",
    "strategy": "hybrid",
    "top_k": 5
})
```

## 🔧 Advanced Features

### Document Chunking Strategies

1. **Semantic Chunking**: Preserves sentence boundaries and meaning
2. **Sentence-based**: Groups sentences intelligently
3. **Sliding Window**: Overlapping chunks for context preservation
4. **Simple**: Character-based chunking

### Search Strategies

1. **Hybrid**: Combines vector and keyword search (recommended)
2. **Vector-only**: Pure semantic similarity
3. **Keyword-only**: Traditional BM25 search

### Configuration

```python
from advanced_rag import create_advanced_rag

# Create with custom settings
rag_processor = create_advanced_rag(
    chunk_size=512,
    chunk_strategy="semantic",
    embedding_model="sentence-transformers/all-MiniLM-L6-v2"
)
```

## 🚀 Deployment

### GitHub Pages (Static)

The application automatically deploys to GitHub Pages via GitHub Actions:

1. Push to `main` branch
2. GitHub Actions builds static content
3. Deploys to GitHub Pages
4. Available at `https://your-username.github.io/enhanced-rag`

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build individual services
docker build -t enhanced-rag .
docker run -p 8000:8000 -e GEMINI_API_KEY=your-key enhanced-rag
```

### Cloud Deployment

The application is cloud-ready and can be deployed to:

- **Heroku**: Use the included `Dockerfile`
- **AWS ECS/Fargate**: Container-ready
- **Google Cloud Run**: Serverless deployment
- **Azure Container Instances**: Easy scaling

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test categories
pytest tests/test_advanced_rag.py -v
```

## 📊 Performance

- **Categorization**: ~3 seconds (Gemini API)
- **Vector Search**: ~0.01 seconds (FAISS)
- **Enhancement**: ~12 seconds (TinyLlama)
- **Total Pipeline**: ~15 seconds per prompt

## 🔒 Security & Privacy

- **Local Enhancement**: TinyLlama runs locally via Ollama
- **API Keys**: Secure environment variable management
- **CORS**: Configurable for production environments
- **Input Validation**: Comprehensive request validation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📋 Roadmap

- [ ] **Multi-modal Support**: Image and video prompt enhancement
- [ ] **Real-time Collaboration**: Multi-user prompt editing
- [ ] **Advanced Analytics**: Usage patterns and optimization insights
- [ ] **Custom Models**: Fine-tuned models for specific domains
- [ ] **API Rate Limiting**: Production-grade rate limiting
- [ ] **Caching Layer**: Redis-based caching for improved performance

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **"The Prompt Report"**: Knowledge base source
- **Google Gemini**: Advanced language model capabilities
- **FAISS**: Efficient vector similarity search
- **Ollama**: Local LLM deployment platform
- **Open Source Community**: Amazing tools and libraries

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/enhanced-rag/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/enhanced-rag/discussions)
- **Documentation**: [Wiki](https://github.com/your-username/enhanced-rag/wiki)

---

**Built with ❤️ for the prompt engineering community**
