FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data with proper error handling
RUN python -c "import nltk; \
    nltk.download('punkt', quiet=True); \
    nltk.download('punkt_tab', quiet=True); \
    nltk.download('stopwords', quiet=True); \
    print('✅ NLTK data downloaded successfully')" || \
    echo "⚠️ NLTK download failed but continuing..."

# Copy application code and ensure all necessary files are included
COPY . .

# Ensure knowledge base vectors are present
RUN ls -la knowledge_base_vectors/ || echo "⚠️ Knowledge base vectors not found"

# Create necessary directories with proper permissions
RUN mkdir -p static logs knowledge_base_vectors && \
    chmod -R 755 static logs knowledge_base_vectors

# Expose ports for FastAPI and Streamlit
EXPOSE 8000 8501

# Environment variables
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Default command - run FastAPI server
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
