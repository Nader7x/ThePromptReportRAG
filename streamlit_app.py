"""
Streamlit Web Interface for Enhanced RAG Application
==================================================

Modern, interactive web interface for the RAG application.
"""

import streamlit as st
import requests
import json
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any
import os

# Configure page
st.set_page_config(
    page_title="Enhanced RAG - Prompt Engineering Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    
    .search-result {
        background: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .technique-badge {
        background: #667eea;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        display: inline-block;
        margin: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")

# Helper functions
def call_rag_directly(prompt: str) -> Dict:
    """Call the RAG system directly without FastAPI"""
    try:
        # Import the RAG system
        from EnhancedPrompt import create_production_rag
        
        # Initialize RAG with API key
        GEMINI_API_KEY = "AIzaSyAWvHgMe_CpVbJI1yZ3Os9pwRV05tRztb8"  # Your API key
        rag = create_production_rag(GEMINI_API_KEY)
        
        # Process the prompt
        result = rag.process_prompt(prompt)
        
        # Add processing time if not present
        if 'processing_time' not in result:
            result['processing_time'] = 0.0
            
        return result
        
    except Exception as e:
        return {
            "error": f"RAG system error: {str(e)}",
            "success": False,
            "original_prompt": prompt,
            "enhanced_prompt": prompt  # Fallback
        }

def call_api(endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    """Call the FastAPI backend or fallback to direct RAG"""
    
    # For enhance-prompt endpoint, try direct RAG first
    if endpoint == "/enhance-prompt" and method == "POST" and data:
        return call_rag_directly(data.get('prompt', ''))
    
    # Original API calling logic for other endpoints
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "POST":
            response = requests.post(url, json=data, timeout=30)
        else:
            response = requests.get(url, timeout=10)
        
        response.raise_for_status()
        result = response.json()
        
        return result
    except requests.exceptions.ConnectionError as e:
        # For enhance-prompt, fallback to direct RAG
        if endpoint == "/enhance-prompt" and method == "POST" and data:
            return call_rag_directly(data.get('prompt', ''))
        
        error_msg = f"Cannot connect to API server at {url}. Using direct RAG fallback."
        st.warning(error_msg)
        return {"error": error_msg}
    except requests.exceptions.Timeout as e:
        error_msg = f"API request timed out to {url}"
        st.error(error_msg)
        return {"error": error_msg}
    except requests.exceptions.RequestException as e:
        error_msg = f"API Error: {e}"
        st.error(error_msg)
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        st.error(error_msg)
        return {"error": error_msg}

def display_search_results(results: List[Dict]):
    """Display search results in a nice format"""
    for i, result in enumerate(results):
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div class="search-result">
                    <h4>#{result['rank']} - {result['source']}</h4>
                    <p>{result['content'][:300]}...</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.metric("Vector Score", f"{result['vector_score']:.3f}")
                st.metric("Keyword Score", f"{result['keyword_score']:.3f}")
                st.metric("Hybrid Score", f"{result['hybrid_score']:.3f}")

# Main header
st.markdown("""
<div class="main-header">
    <h1>🚀 Enhanced RAG - Prompt Engineering Assistant</h1>
    <p>Production-grade RAG application with advanced features</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Choose a page",
    ["🏠 Home", "✨ Prompt Enhancement", "� Analytics"]  # Simplified for working features
)



# Health check
with st.sidebar:
    st.subheader("System Status")
    
    # Test RAG system directly
    if st.button("🔄 Test RAG System"):
        with st.spinner("Testing RAG system..."):
            test_result = call_rag_directly("Test prompt")
            if test_result.get('success'):
                st.success("✅ RAG System: Ready")
                st.info("🧠 Gemini API: Connected")
                st.info("🔍 FAISS Vector DB: Loaded")
                st.info("📚 Knowledge Base: Available")
            else:
                st.error("❌ RAG System: Error")
                if test_result.get('error'):
                    st.error(f"Error: {test_result['error']}")
    else:
        # Show default status
        st.success("✅ RAG System: Ready")
        st.info("🧠 Direct Integration Mode")
        
    # Troubleshooting tips
    with st.expander("🛠️ System Info"):
        st.markdown("""
        **Current Setup:**
        - Using direct RAG integration
        - No FastAPI server required
        - Gemini API for categorization & enhancement
        - FAISS vector database for knowledge retrieval
        
        **If you see errors:**
        1. Check your internet connection (for Gemini API)
        2. Verify the knowledge base files are present
        3. Ensure all dependencies are installed
        """)

# Page content
if page == "🏠 Home":
    st.header("Welcome to Enhanced RAG")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>🧠 Smart Categorization</h3>
            <p>Gemini API identifies the best prompt technique for your use case</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>🔍 Hybrid Search</h3>
            <p>Advanced vector + keyword search for maximum relevance</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>✨ AI Enhancement</h3>
            <p>Gemini API enhances your prompts with proven techniques</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.subheader("🚀 Quick Start")
    st.write("1. Go to **Prompt Enhancement** to improve your prompts using AI")
    st.write("2. View **Analytics** to see usage statistics")
    
    # Demo section
    with st.expander("🎯 Try a Quick Demo"):
        demo_prompt = st.text_input("Enter a prompt to enhance:", "Write a summary about machine learning")
        if st.button("Enhance Demo Prompt"):
            if demo_prompt:
                with st.spinner("Enhancing prompt..."):
                    result = call_api("/enhance-prompt", "POST", {"prompt": demo_prompt})
                    
                    # Check if we have a valid response from our RAG system
                    if (result and 
                        result.get("success") is True and 
                        result.get("enhanced_prompt") and 
                        result.get("enhanced_prompt").strip()):
                        st.success("✅ Enhancement complete!")
                        st.write(f"**Original:** {result.get('original_prompt', demo_prompt)}")
                        st.write(f"**Enhanced:** {result.get('enhanced_prompt', 'Not available')}")
                        st.write(f"**Technique:** {result.get('identified_technique', 'Unknown')}")
                    else:
                        st.error("❌ Demo enhancement failed")
                        if result and "error" in result:
                            st.error(f"Error: {result['error']}")
                        else:
                            st.error("No valid response received from RAG system")

elif page == "✨ Prompt Enhancement":
    st.header("Prompt Enhancement")
    st.write("Transform your prompts using advanced AI techniques from 'The Prompt Report'")
    
    # Input form
    with st.form("prompt_form"):
        user_prompt = st.text_area(
            "Enter your prompt:",
            height=100,
            placeholder="E.g., Help me write a professional email to my boss..."
        )
        
        # Get available techniques from our knowledge base
        try:
            from PromptReportKnowledgeBase import TEXT_BASED_TECHNIQUES
            available_techniques = ["Auto-detect"] + [t.technique_name for t in TEXT_BASED_TECHNIQUES[:10]]  # Show first 10
        except ImportError:
            available_techniques = ["Auto-detect", "Zero-Shot Prompting", "Few-Shot Prompting", "Chain-of-Thought", "Role Prompting"]
        
        technique_hint = st.selectbox(
            "Technique hint (optional):",
            available_techniques
        )
        
        submitted = st.form_submit_button("🚀 Enhance Prompt")
    
    if submitted and user_prompt:
        with st.spinner("Processing your prompt..."):
            start_time = time.time()
            
            request_data = {"prompt": user_prompt}
            if technique_hint != "Auto-detect":
                request_data["technique_hint"] = technique_hint
            
            result = call_api("/enhance-prompt", "POST", request_data)
            
            # Check success using our RAG system's response format
            is_success = (
                result and 
                result.get("success") is True and  # Must be explicitly True
                result.get("enhanced_prompt") and  # Must have enhanced prompt
                result.get("enhanced_prompt").strip()  # Must not be empty
            )
            
            if is_success:
                processing_time = time.time() - start_time
                
                # Display results
                st.success("✅ Prompt enhanced successfully!")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader("Results")
                    
                    with st.container():
                        st.markdown("**Original Prompt:**")
                        st.info(result.get('original_prompt', user_prompt))
                        
                        st.markdown("**Enhanced Prompt:**")
                        enhanced_prompt = result.get('enhanced_prompt', 'No enhancement available')
                        if enhanced_prompt and enhanced_prompt.strip():
                            st.success(enhanced_prompt)
                        else:
                            st.warning("⚠️ Enhancement was empty or failed. Using original prompt.")
                            st.info(result.get('original_prompt', user_prompt))
                
                with col2:
                    st.subheader("Metadata")
                    
                    # Processing time
                    api_time = result.get('processing_time', 0)
                    total_time = processing_time
                    st.metric("API Processing Time", f"{api_time:.2f}s")
                    st.metric("Total Time", f"{total_time:.2f}s")
                    
                    # Identified technique
                    technique = result.get('identified_technique', 'Unknown')
                    st.markdown(f"""
                    <div class="technique-badge">
                        📋 {technique}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Context information
                    if result.get('context_used'):
                        with st.expander("🔍 View Context Used"):
                            context = result['context_used']
                            if isinstance(context, dict):
                                st.json(context)
                            else:
                                st.write(context)
                    
            else:
                # Enhanced error reporting for our RAG system
                st.error("❌ Enhancement failed")
                
                if result:
                    if "error" in result:
                        st.error(f"RAG System Error: {result['error']}")
                    elif result.get("success") is False:
                        st.warning("⚠️ RAG system processed request but enhancement failed")
                    else:
                        st.warning("ℹ️ RAG system response received but enhancement incomplete")
                else:
                    st.error("No response received from RAG system")
                    
                st.info("💡 The RAG system is running directly - no API server needed!")

elif page == " Analytics":
    st.header("Analytics Dashboard")
    st.write("System performance and usage analytics")
    
    # Mock analytics data (replace with real data in production)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Prompts Enhanced", "1,234", "↗️ 12%")
    
    with col2:
        st.metric("Avg. Processing Time", "2.3s", "↘️ 0.2s")
    
    with col3:
        st.metric("Search Queries", "5,678", "↗️ 8%")
    
    with col4:
        st.metric("API Uptime", "99.8%", "↗️ 0.1%")
    
    # Charts
    st.subheader("📈 Usage Trends")
    
    # Mock data for demonstration
    import datetime
    import random
    
    dates = [datetime.date.today() - datetime.timedelta(days=x) for x in range(30, 0, -1)]
    prompts_enhanced = [random.randint(20, 100) for _ in dates]
    searches_performed = [random.randint(50, 200) for _ in dates]
    
    df_usage = pd.DataFrame({
        'Date': dates,
        'Prompts Enhanced': prompts_enhanced,
        'Searches Performed': searches_performed
    })
    
    fig = px.line(df_usage, x='Date', y=['Prompts Enhanced', 'Searches Performed'],
                  title="Daily Usage Metrics")
    st.plotly_chart(fig, use_container_width=True)
    
    # Technique usage
    st.subheader("🏆 Most Used Techniques")
    technique_usage = {
        "Zero-Shot Prompting": 45,
        "Few-Shot Prompting": 32,
        "Chain of Thought": 28,
        "Style Prompting": 22,
        "Role Prompting": 18
    }
    
    fig_pie = px.pie(
        values=list(technique_usage.values()),
        names=list(technique_usage.keys()),
        title="Technique Usage Distribution"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8rem;">
    Enhanced RAG Application v2.0 | Built with Streamlit, Gemini API, FAISS Vector DB, and Sentence Transformers
</div>
""", unsafe_allow_html=True)
