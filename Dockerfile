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
RUN pip install uv
RUN uv venv && . .venv/bin/activate
RUN uv pip install --no-cache-dir -r requirements.txt

# Ensure NLTK is available and download required data
RUN . .venv/bin/activate && python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p static logs

# Expose ports for FastAPI and Streamlit
EXPOSE 8000 8501

# Environment variables
ENV PYTHONPATH=/app
# Note: GEMINI_API_KEY should be set via environment variable or docker-compose
# ENV API_BASE_URL="http://localhost:8000/api"

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Default command (can be overridden)
CMD ["python", "api.py"]
