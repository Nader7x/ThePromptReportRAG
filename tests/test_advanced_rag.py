"""
Test suite for Enhanced RAG Application
======================================

Comprehensive tests for all components of the RAG application.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from advanced_rag import (
    AdvancedChunker, 
    HybridRetriever, 
    AdvancedRAGProcessor,
    DocumentChunk,
    SearchResult,
    create_advanced_rag
)
from PromptReportKnowledgeBase import export_knowledge_base

class TestAdvancedChunker:
    """Test the advanced document chunker"""
    
    @pytest.fixture
    def sample_text(self):
        return """
        This is a test document. It contains multiple sentences.
        Each sentence should be processed correctly. The chunker should handle
        different strategies effectively. This includes semantic chunking,
        sentence-based chunking, and sliding window approaches.
        
        The advanced chunker is designed to split large documents into
        manageable pieces while preserving context and meaning.
        """
    
    @pytest.fixture
    def chunker(self):
        return AdvancedChunker(chunk_size=100, chunk_overlap=20, strategy="semantic")
    
    def test_semantic_chunking(self, chunker, sample_text):
        """Test semantic chunking strategy"""
        chunks = chunker.chunk_document(sample_text, "test_doc")
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, DocumentChunk) for chunk in chunks)
        assert all(chunk.source == "test_doc" for chunk in chunks)
        assert all(chunk.content.strip() for chunk in chunks)
    
    def test_sentence_chunking(self, sample_text):
        """Test sentence-based chunking"""
        chunker = AdvancedChunker(chunk_size=150, strategy="sentence")
        chunks = chunker.chunk_document(sample_text, "test_doc")
        
        assert len(chunks) > 0
        for chunk in chunks:
            assert chunk.metadata.get("sentence_count", 0) > 0
    
    def test_sliding_window_chunking(self, sample_text):
        """Test sliding window chunking"""
        chunker = AdvancedChunker(chunk_size=80, chunk_overlap=20, strategy="sliding_window")
        chunks = chunker.chunk_document(sample_text, "test_doc")
        
        assert len(chunks) > 0
        for chunk in chunks:
            assert len(chunk.content) <= 80 or chunk.content.count(' ') < 2  # Allow for word boundaries
    
    def test_simple_chunking(self, sample_text):
        """Test simple character-based chunking"""
        chunker = AdvancedChunker(chunk_size=50, strategy="simple")
        chunks = chunker.chunk_document(sample_text, "test_doc")
        
        assert len(chunks) > 0
        for chunk in chunks:
            assert chunk.metadata.get("simple_chunk") is True

class TestHybridRetriever:
    """Test the hybrid retriever"""
    
    @pytest.fixture
    def sample_chunks(self):
        """Create sample document chunks for testing"""
        chunks = [
            DocumentChunk(
                content="Few-shot prompting involves providing examples in the prompt.",
                chunk_id="chunk_1",
                source="technique_1",
                start_pos=0,
                end_pos=50,
                metadata={"technique": "few_shot"}
            ),
            DocumentChunk(
                content="Chain of thought prompting encourages step-by-step reasoning.",
                chunk_id="chunk_2", 
                source="technique_2",
                start_pos=0,
                end_pos=50,
                metadata={"technique": "chain_of_thought"}
            ),
            DocumentChunk(
                content="Zero-shot prompting works without any examples provided.",
                chunk_id="chunk_3",
                source="technique_3", 
                start_pos=0,
                end_pos=50,
                metadata={"technique": "zero_shot"}
            )
        ]
        return chunks
    
    @pytest.fixture
    def retriever(self):
        return HybridRetriever(vector_weight=0.7, keyword_weight=0.3)
    
    def test_build_indices(self, retriever, sample_chunks):
        """Test building search indices"""
        retriever.build_indices(sample_chunks)
        
        assert retriever.vector_index is not None
        assert retriever.bm25 is not None
        assert retriever.tfidf_vectorizer is not None
        assert len(retriever.chunks) == len(sample_chunks)
        assert len(retriever.documents) == len(sample_chunks)
    
    def test_vector_search(self, retriever, sample_chunks):
        """Test vector-only search"""
        retriever.build_indices(sample_chunks)
        
        results = retriever.hybrid_search(
            "examples in prompts", 
            top_k=2, 
            vector_weight=1.0, 
            keyword_weight=0.0
        )
        
        assert len(results) <= 2
        assert all(isinstance(result, SearchResult) for result in results)
        assert all(result.vector_score > 0 for result in results)
    
    def test_keyword_search(self, retriever, sample_chunks):
        """Test keyword-only search"""
        retriever.build_indices(sample_chunks)
        
        results = retriever.hybrid_search(
            "reasoning step", 
            top_k=2, 
            vector_weight=0.0, 
            keyword_weight=1.0
        )
        
        assert len(results) <= 2
        assert all(isinstance(result, SearchResult) for result in results)
    
    def test_hybrid_search(self, retriever, sample_chunks):
        """Test hybrid search combining vector and keyword"""
        retriever.build_indices(sample_chunks)
        
        results = retriever.hybrid_search("prompting techniques", top_k=3)
        
        assert len(results) <= 3
        assert all(isinstance(result, SearchResult) for result in results)
        assert all(hasattr(result, 'hybrid_score') for result in results)
        assert all(result.rank > 0 for result in results)

class TestAdvancedRAGProcessor:
    """Test the complete advanced RAG processor"""
    
    @pytest.fixture
    def rag_processor(self):
        chunker = AdvancedChunker(chunk_size=200, strategy="semantic")
        retriever = HybridRetriever()
        return AdvancedRAGProcessor(chunker, retriever)
    
    @pytest.fixture
    def sample_documents(self):
        return {
            "few_shot_prompting": "Few-shot prompting is a technique where you provide examples.",
            "chain_of_thought": "Chain of thought prompting involves step-by-step reasoning.",
            "zero_shot": "Zero-shot prompting works without providing examples."
        }
    
    def test_process_documents(self, rag_processor, sample_documents):
        """Test processing multiple documents"""
        chunks = rag_processor.process_documents(sample_documents)
        
        assert len(chunks) >= len(sample_documents)  # Could be more due to chunking
        assert all(isinstance(chunk, DocumentChunk) for chunk in chunks)
        
        # Check that all documents are represented
        sources = {chunk.source for chunk in chunks}
        assert sources == set(sample_documents.keys())
    
    def test_enhanced_search_strategies(self, rag_processor, sample_documents):
        """Test different search strategies"""
        rag_processor.process_documents(sample_documents)
        
        # Test hybrid search
        results_hybrid = rag_processor.enhanced_search("examples", search_strategy="hybrid")
        assert len(results_hybrid) > 0
        
        # Test vector-only search
        results_vector = rag_processor.enhanced_search("examples", search_strategy="vector_only")
        assert len(results_vector) > 0
        
        # Test keyword-only search
        results_keyword = rag_processor.enhanced_search("examples", search_strategy="keyword_only")
        assert len(results_keyword) > 0

class TestKnowledgeBaseIntegration:
    """Test integration with the knowledge base"""
    
    def test_knowledge_base_export(self):
        """Test that knowledge base can be exported"""
        kb = export_knowledge_base()
        
        assert isinstance(kb, dict)
        assert len(kb) > 0
        
        # Check structure of exported data
        assert 'text_based_techniques' in kb
        assert 'prompt_engineering_techniques' in kb
        assert isinstance(kb['text_based_techniques'], list)
        assert len(kb['text_based_techniques']) > 0
    
    def test_knowledge_base_with_rag(self):
        """Test using knowledge base with RAG processor"""
        rag_processor = create_advanced_rag()
        kb = export_knowledge_base()
        
        # Process knowledge base documents (using correct structure)
        documents = {}
        
        # Process text-based techniques
        for technique in kb.get('text_based_techniques', []):
            name = technique.get('technique_name', 'Unknown')
            content = f"{technique.get('definition', '')} {technique.get('description', '')}"
            if content.strip():
                documents[name] = content
        
        if documents:  # Only test if we have documents
            chunks = rag_processor.process_documents(documents)
            assert len(chunks) > 0
            
            # Test search
            results = rag_processor.enhanced_search("few shot examples")
            assert len(results) > 0

class TestAPIComponents:
    """Test API-related components"""
    
    def test_create_advanced_rag_factory(self):
        """Test the factory function"""
        rag_processor = create_advanced_rag(
            chunk_size=256,
            chunk_strategy="sentence"
        )
        
        assert isinstance(rag_processor, AdvancedRAGProcessor)
        assert rag_processor.chunker.chunk_size == 256
        assert rag_processor.chunker.strategy == "sentence"

@pytest.mark.integration
class TestIntegration:
    """Integration tests for the complete system"""
    
    def test_end_to_end_processing(self):
        """Test complete end-to-end processing"""
        # Create RAG processor
        rag_processor = create_advanced_rag()
        
        # Sample documents
        documents = {
            "test_technique": "This is a test technique for prompting with examples and reasoning."
        }
        
        # Process documents
        chunks = rag_processor.process_documents(documents)
        assert len(chunks) > 0
        
        # Search for relevant information
        results = rag_processor.enhanced_search("examples reasoning", top_k=1)
        assert len(results) > 0
        
        # Verify result structure
        result = results[0]
        assert hasattr(result, 'content')
        assert hasattr(result, 'hybrid_score')
        assert hasattr(result, 'rank')

# Test configuration
@pytest.fixture(scope="session")
def test_config():
    """Test configuration for the entire test suite"""
    return {
        "chunk_size": 100,
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "vector_weight": 0.7,
        "keyword_weight": 0.3
    }

if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v"])
