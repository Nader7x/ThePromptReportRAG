"""
Basic tests for the Enhanced RAG Application
"""

import pytest
import os
import sys

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_import_basic_modules():
    """Test that basic modules can be imported"""
    try:
        import PromptReportKnowledgeBase
        import EnhancedPrompt
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import basic modules: {e}")

def test_knowledge_base_export():
    """Test knowledge base export functionality"""
    from PromptReportKnowledgeBase import export_knowledge_base
    
    kb = export_knowledge_base()
    assert isinstance(kb, dict)
    assert 'text_based_techniques' in kb
    assert len(kb['text_based_techniques']) > 0

def test_rag_config():
    """Test RAG configuration"""
    from EnhancedPrompt import RAGConfig
    
    config = RAGConfig(gemini_api_key="test_key")
    assert config.gemini_api_key == "test_key"
    assert config.ollama_base_url == "http://localhost:11434"

def test_advanced_rag_import():
    """Test advanced RAG imports"""
    try:
        import advanced_rag
        from advanced_rag import AdvancedChunker, HybridRetriever
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import advanced RAG modules: {e}")

if __name__ == "__main__":
    pytest.main([__file__])
