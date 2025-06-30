"""
FastAPI Backend for Enhanced RAG Application
===========================================

This module provides REST API endpoints for the RAG application.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from advanced_rag import create_advanced_rag

# Import our RAG components
from EnhancedPrompt import create_production_rag
from PromptReportKnowledgeBase import export_knowledge_base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Enhanced RAG API",
    description="Production-grade RAG application for prompt engineering",
    version="3.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global RAG instances
production_rag = None
advanced_rag_processor = None


# Pydantic models for API
class PromptRequest(BaseModel):
    prompt: str = Field(..., description="The user prompt to enhance")
    technique_hint: Optional[str] = Field(None, description="Optional technique hint")


class PromptResponse(BaseModel):
    original_prompt: str
    enhanced_prompt: str
    identified_technique: str
    success: bool
    processing_time: float
    context_used: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    strategy: str = Field("hybrid", description="Search strategy: hybrid, vector_only, keyword_only")
    top_k: int = Field(5, description="Number of results to return")


class SearchResponse(BaseModel):
    query: str
    results: List[Dict[str, Any]]
    total_results: int
    search_time: float


class DocumentUpload(BaseModel):
    content: str = Field(..., description="Document content")
    title: str = Field(..., description="Document title")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    services: Dict[str, str]


# Initialize RAG components
@app.on_event("startup")
async def startup_event():
    global production_rag, advanced_rag_processor

    try:
        logger.info("=== Starting Enhanced RAG Application ===")
        
        # Get API key from environment
        gemini_api_key = os.getenv("GEMINI_API_KEY", "AIzaSyAWvHgMe_CpVbJI1yZ3Os9pwRV05tRztb8")
        
        # Validate API key
        if not gemini_api_key or gemini_api_key in ["test-key-placeholder", ""]:
            logger.warning("⚠️ No valid GEMINI_API_KEY found - some features may not work")
        else:
            logger.info("✅ GEMINI_API_KEY configured")

        # Check if knowledge base vectors exist
        vector_path = Path("knowledge_base_vectors")
        if vector_path.exists():
            logger.info(f"✅ Knowledge base vectors found at {vector_path}")
            for file in vector_path.iterdir():
                logger.info(f"  - {file.name} ({file.stat().st_size} bytes)")
        else:
            logger.warning(f"⚠️ Knowledge base vectors not found at {vector_path}")

        # Initialize production RAG with error handling
        logger.info("🚀 Initializing production RAG...")
        try:
            production_rag = create_production_rag(gemini_api_key)
            logger.info("✅ Production RAG initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize production RAG: {e}")
            logger.error(f"Error details: {type(e).__name__}: {str(e)}")
            # Don't fail startup completely, allow partial functionality
            production_rag = None

        # Initialize advanced RAG processor with error handling
        logger.info("🚀 Initializing advanced RAG processor...")
        try:
            advanced_rag_processor = create_advanced_rag()
            logger.info("✅ Advanced RAG processor initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize advanced RAG processor: {e}")
            logger.error(f"Error details: {type(e).__name__}: {str(e)}")
            # Don't fail startup completely
            advanced_rag_processor = None

        # Process knowledge base documents if advanced RAG is available
        if advanced_rag_processor:
            logger.info("📚 Processing knowledge base documents...")
            try:
                knowledge_base = export_knowledge_base()
                documents = {}

                # Process text-based techniques
                for technique in knowledge_base.get("text_based_techniques", []):
                    technique_name = technique.get("technique_name", "Unknown")
                    doc_content = f"{technique.get('definition', '')} {technique.get('description', '')} {' '.join(technique.get('examples', []))}"
                    documents[technique_name] = doc_content

                # Process other technique types as well
                for pe_technique in knowledge_base.get("prompt_engineering_techniques", []):
                    technique_name = pe_technique.get("technique_name", "Unknown")
                    doc_content = f"{pe_technique.get('definition', '')} {pe_technique.get('description', '')} {' '.join(pe_technique.get('examples', []))}"
                    documents[technique_name] = doc_content

                if documents:
                    advanced_rag_processor.process_documents(documents)
                    logger.info(f"✅ Processed {len(documents)} knowledge base documents")
                else:
                    logger.warning("⚠️ No documents found in knowledge base")
                    
            except Exception as e:
                logger.error(f"❌ Failed to process knowledge base documents: {e}")
                logger.error(f"Error details: {type(e).__name__}: {str(e)}")

        logger.info("=== RAG Application Startup Complete ===")
        
        # Log final status
        status_summary = []
        if production_rag:
            status_summary.append("✅ Production RAG: Ready")
        else:
            status_summary.append("❌ Production RAG: Failed")
            
        if advanced_rag_processor:
            status_summary.append("✅ Advanced RAG: Ready")
        else:
            status_summary.append("❌ Advanced RAG: Failed")
            
        logger.info("📊 Startup Summary:")
        for status in status_summary:
            logger.info(f"  {status}")

    except Exception as e:
        logger.error(f"💥 Critical startup error: {e}")
        logger.error(f"Error details: {type(e).__name__}: {str(e)}")
        # In production, you might want to raise this to prevent the app from starting
        # raise  # Uncomment to fail fast on startup errors


# Health check endpoint
@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with detailed diagnostic information"""
    try:
        # Check core services
        services = {
            "rag": "healthy" if production_rag else "unhealthy",
            "advanced_rag": "healthy" if advanced_rag_processor else "unhealthy",
            "gemini_api": "configured" if os.getenv("GEMINI_API_KEY") else "not_configured",
        }
        
        # Check filesystem
        vector_path = Path("knowledge_base_vectors")
        services["vector_store"] = "available" if vector_path.exists() else "missing"
        
        # Check if we can import key dependencies
        try:
            import sentence_transformers
            import faiss
            import google.generativeai
            services["dependencies"] = "available"
        except ImportError as e:
            services["dependencies"] = f"missing: {str(e)}"
        
        # Determine overall status
        critical_services = ["rag", "dependencies"]
        overall_status = "healthy"
        
        if any(services.get(service) == "unhealthy" for service in critical_services):
            overall_status = "unhealthy"
        elif any(services.get(service, "").startswith("missing") for service in services):
            overall_status = "degraded"

        return HealthResponse(
            status=overall_status,
            timestamp=datetime.now().isoformat(),
            services=services,
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="error",
            timestamp=datetime.now().isoformat(),
            services={"error": str(e)},
        )


# Main RAG endpoint
@app.post("/api/enhance-prompt", response_model=PromptResponse)
async def enhance_prompt(request: PromptRequest):
    """Enhance a user prompt using the RAG pipeline"""
    if not production_rag:
        raise HTTPException(status_code=503, detail="RAG service not initialized")

    try:
        start_time = datetime.now()

        # Process the prompt
        result = production_rag.process_prompt(request.prompt)

        processing_time = (datetime.now() - start_time).total_seconds()

        return PromptResponse(
            original_prompt=result["original_prompt"],
            enhanced_prompt=result["enhanced_prompt"],
            identified_technique=result.get("identified_technique", "unknown"),
            success=result["success"],
            processing_time=processing_time,
            context_used=result.get("context_used"),
            error=result.get("error"),
        )

    except Exception as e:
        logger.error(f"Error enhancing prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Advanced search endpoint
@app.post("/api/search", response_model=SearchResponse)
async def search_knowledge(request: SearchRequest):
    """Search the knowledge base using advanced hybrid search"""
    if not advanced_rag_processor:
        raise HTTPException(status_code=503, detail="Advanced RAG service not initialized")

    try:
        start_time = datetime.now()

        # Perform search
        results = advanced_rag_processor.enhanced_search(
            query=request.query, search_strategy=request.strategy, top_k=request.top_k
        )

        search_time = (datetime.now() - start_time).total_seconds()

        # Convert results to dict format
        result_dicts = []
        for result in results:
            result_dicts.append(
                {
                    "content": result.content,
                    "source": result.source,
                    "vector_score": result.vector_score,
                    "keyword_score": result.keyword_score,
                    "hybrid_score": result.hybrid_score,
                    "rank": result.rank,
                    "metadata": result.metadata,
                }
            )

        return SearchResponse(
            query=request.query, results=result_dicts, total_results=len(result_dicts), search_time=search_time
        )

    except Exception as e:
        logger.error(f"Error in search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Knowledge base endpoints
@app.get("/api/techniques")
async def get_techniques():
    """Get all available prompt techniques"""
    try:
        knowledge_base = export_knowledge_base()
        return {"techniques": list(knowledge_base.keys()), "total_count": len(knowledge_base)}
    except Exception as e:
        logger.error(f"Error getting techniques: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/techniques/{technique_name}")
async def get_technique_details(technique_name: str):
    """Get details for a specific technique"""
    try:
        knowledge_base = export_knowledge_base()
        if technique_name not in knowledge_base:
            raise HTTPException(status_code=404, detail="Technique not found")

        return knowledge_base[technique_name]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting technique details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Document processing endpoint
@app.post("/api/documents/process")
async def process_document(document: DocumentUpload, background_tasks: BackgroundTasks):
    """Process a new document for the knowledge base"""
    try:
        # This is a placeholder for document processing
        # In a real implementation, you'd want to:
        # 1. Validate the document
        # 2. Chunk it using advanced_rag_processor
        # 3. Update the search indices
        # 4. Store it persistently

        background_tasks.add_task(_process_document_background, document.content, document.title, document.metadata)

        return {"message": "Document processing started", "title": document.title, "status": "processing"}
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _process_document_background(content: str, title: str, metadata: dict):
    """Background task for document processing"""
    try:
        # Placeholder for background processing
        logger.info(f"Processing document: {title}")
        # Add actual document processing logic here
    except Exception as e:
        logger.error(f"Background document processing failed: {e}")


# Serve static files (for web interface)
app.mount("/static", StaticFiles(directory="static"), name="static")


# Serve the web interface
@app.get("/", response_class=HTMLResponse)
async def serve_web_interface():
    """Serve the main web interface"""
    try:
        with open("static/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="""
        <html>
            <head><title>Enhanced RAG API</title></head>
            <body>
                <h1>Enhanced RAG API</h1>
                <p>API is running. Visit <a href="/api/docs">/api/docs</a> for API documentation.</p>
                <p>Web interface files not found. Please create the static files.</p>
            </body>
        </html>
        """
        )


# Development server
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
