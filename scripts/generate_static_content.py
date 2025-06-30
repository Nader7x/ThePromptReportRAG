"""
Generate static content for GitHub Pages deployment
=================================================

This script creates additional static content for GitHub Pages deployment.
"""

import json
import os
from pathlib import Path
from PromptReportKnowledgeBase import export_knowledge_base


def generate_knowledge_base_json():
    """Generate knowledge base as JSON for static access"""
    kb = export_knowledge_base()

    # Create build directory if it doesn't exist
    build_dir = Path("build")
    build_dir.mkdir(exist_ok=True)

    # Save knowledge base as JSON
    with open(build_dir / "knowledge_base.json", "w") as f:
        json.dump(kb, f, indent=2, default=str)

    # Create techniques list
    techniques_list = {"techniques": list(kb.keys()), "total_count": len(kb), "categories": {}}

    # Categorize techniques (if category info available)
    for name, details in kb.items():
        category = details.get("category", "General")
        if category not in techniques_list["categories"]:
            techniques_list["categories"][category] = []
        techniques_list["categories"][category].append(name)

    with open(build_dir / "techniques.json", "w") as f:
        json.dump(techniques_list, f, indent=2)


def generate_api_manifest():
    """Generate API manifest for static deployment"""
    manifest = {
        "name": "Enhanced RAG API",
        "version": "3.0.0",
        "description": "Production-grade RAG application for prompt engineering",
        "endpoints": {
            "/api/health": "Health check endpoint",
            "/api/enhance-prompt": "Enhance user prompts",
            "/api/search": "Search knowledge base",
            "/api/techniques": "List all techniques",
            "/api/techniques/{name}": "Get technique details",
        },
        "features": [
            "Gemini API integration",
            "FAISS vector search",
            "Hybrid search (vector + keyword)",
            "Advanced document chunking",
            "TinyLlama enhancement",
        ],
        "deployment": {"type": "static", "platform": "GitHub Pages", "build_date": "2025-06-25"},
    }

    build_dir = Path("build")
    with open(build_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)


def create_static_demo():
    """Create a static demo page"""
    demo_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced RAG - Static Demo</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #667eea;
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .feature-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        .demo-section {
            background: #e8f5e8;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .code-block {
            background: #2d3748;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
        }
        .btn {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 10px 5px;
        }
        .technique-list {
            max-height: 300px;
            overflow-y: auto;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Enhanced RAG</h1>
            <p>Production-grade Prompt Engineering Assistant</p>
            <p><em>Static Demo - GitHub Pages Deployment</em></p>
        </div>

        <div class="demo-section">
            <h2>🎯 About This Application</h2>
            <p>This is a production-grade RAG (Retrieval-Augmented Generation) application that enhances user prompts using advanced AI techniques from "The Prompt Report".</p>
            
            <div class="feature-grid">
                <div class="feature-card">
                    <h3>🧠 Smart Categorization</h3>
                    <p>Uses Gemini API to identify the most relevant prompt engineering technique for your specific use case.</p>
                </div>
                <div class="feature-card">
                    <h3>🔍 Hybrid Search</h3>
                    <p>Combines FAISS vector search with BM25 keyword search for maximum relevance and accuracy.</p>
                </div>
                <div class="feature-card">
                    <h3>✨ AI Enhancement</h3>
                    <p>Google Gemini API enhances your prompts with proven techniques from research using advanced AI.</p>
                </div>
                <div class="feature-card">
                    <h3>📚 Knowledge Base</h3>
                    <p>Comprehensive database of prompt engineering techniques from "The Prompt Report".</p>
                </div>
            </div>
        </div>

        <div class="demo-section">
            <h2>🛠️ Technical Architecture</h2>
            <div class="code-block">
User Prompt → Gemini API → FAISS Vector DB → TinyLlama → Enhanced Prompt
              (Categorize)   (Retrieve)      (Enhance)
            </div>
            
            <h3>Technologies Used:</h3>
            <ul>
                <li><strong>FastAPI:</strong> High-performance web framework for API</li>
                <li><strong>Streamlit:</strong> Interactive web interface</li>
                <li><strong>FAISS:</strong> Facebook's vector similarity search</li>
                <li><strong>Sentence Transformers:</strong> State-of-the-art embeddings</li>
                <li><strong>Gemini API:</strong> Google's advanced language model for categorization and enhancement</li>
                <li><strong>GitHub Actions:</strong> CI/CD and deployment</li>
            </ul>
        </div>

        <div class="demo-section">
            <h2>📊 Features Implemented</h2>
            <ul>
                <li>✅ Advanced document chunking with multiple strategies</li>
                <li>✅ Hybrid search combining vector and keyword approaches</li>
                <li>✅ Production-ready FastAPI backend with full documentation</li>
                <li>✅ Modern Streamlit web interface</li>
                <li>✅ Docker containerization for easy deployment</li>
                <li>✅ GitHub Actions CI/CD pipeline</li>
                <li>✅ Comprehensive error handling and logging</li>
                <li>✅ RESTful API with OpenAPI documentation</li>
            </ul>
        </div>

        <div class="demo-section">
            <h2>🚀 Quick Start</h2>
            <p>To run this application locally:</p>
            <div class="code-block">
# Clone the repository
git clone &lt;repository-url&gt;
cd enhanced-rag

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY="your-api-key"

# Run the API server
python api.py

# Run the Streamlit interface (in another terminal)
streamlit run streamlit_app.py
            </div>
        </div>

        <div class="demo-section">
            <h2>📚 Available Techniques</h2>
            <div id="techniquesList" class="technique-list">
                Loading techniques...
            </div>
        </div>

        <div style="text-align: center; margin-top: 30px;">
            <a href="/" class="btn">🏠 Back to Main Interface</a>
            <a href="/api/docs" class="btn">📖 API Documentation</a>
        </div>
    </div>

    <script>
        // Load techniques from JSON file
        fetch('./techniques.json')
            .then(response => response.json())
            .then(data => {
                const list = document.getElementById('techniquesList');
                let html = `<p><strong>Total Techniques:</strong> ${data.total_count}</p><ul>`;
                data.techniques.forEach(technique => {
                    html += `<li>${technique}</li>`;
                });
                html += '</ul>';
                list.innerHTML = html;
            })
            .catch(error => {
                document.getElementById('techniquesList').innerHTML = 
                    '<p>Error loading techniques. Please check the API.</p>';
            });
    </script>
</body>
</html>
    """

    build_dir = Path("build")
    with open(build_dir / "demo.html", "w") as f:
        f.write(demo_html)


def main():
    """Generate all static content"""
    print("Generating static content for GitHub Pages...")

    try:
        generate_knowledge_base_json()
        print("✅ Generated knowledge base JSON")

        generate_api_manifest()
        print("✅ Generated API manifest")

        create_static_demo()
        print("✅ Created static demo page")

        print("🚀 Static content generation complete!")

    except Exception as e:
        print(f"❌ Error generating static content: {e}")
        raise


if __name__ == "__main__":
    main()
