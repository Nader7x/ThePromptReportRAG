"""
Generate API documentation for static deployment
==============================================

This script generates comprehensive API documentation.
"""

import json
from pathlib import Path
from datetime import datetime


def generate_api_docs():
    """Generate comprehensive API documentation"""

    api_docs = {
        "openapi": "3.0.0",
        "info": {
            "title": "Enhanced RAG API",
            "description": "Production-grade RAG application for prompt engineering",
            "version": "3.0.0",
            "contact": {"name": "Enhanced RAG Team", "url": "https://github.com/your-username/enhanced-rag"},
        },
        "servers": [
            {"url": "https://your-username.github.io/enhanced-rag", "description": "GitHub Pages Deployment"},
            {"url": "http://localhost:8000", "description": "Local Development"},
        ],
        "paths": {
            "/api/health": {
                "get": {
                    "summary": "Health Check",
                    "description": "Check the health status of the API and its services",
                    "responses": {
                        "200": {
                            "description": "Health status",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "timestamp": {"type": "string"},
                                            "services": {"type": "object", "additionalProperties": {"type": "string"}},
                                        },
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/api/enhance-prompt": {
                "post": {
                    "summary": "Enhance Prompt",
                    "description": "Enhance a user prompt using the RAG pipeline",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "prompt": {"type": "string", "description": "The user prompt to enhance"},
                                        "technique_hint": {"type": "string", "description": "Optional technique hint"},
                                    },
                                    "required": ["prompt"],
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Enhanced prompt result",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "original_prompt": {"type": "string"},
                                            "enhanced_prompt": {"type": "string"},
                                            "identified_technique": {"type": "string"},
                                            "success": {"type": "boolean"},
                                            "processing_time": {"type": "number"},
                                            "context_used": {"type": "object"},
                                            "error": {"type": "string"},
                                        },
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/api/search": {
                "post": {
                    "summary": "Search Knowledge Base",
                    "description": "Search the knowledge base using hybrid search",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "query": {"type": "string"},
                                        "strategy": {
                                            "type": "string",
                                            "enum": ["hybrid", "vector_only", "keyword_only"],
                                            "default": "hybrid",
                                        },
                                        "top_k": {"type": "integer", "minimum": 1, "maximum": 20, "default": 5},
                                    },
                                    "required": ["query"],
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Search results",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "query": {"type": "string"},
                                            "results": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "content": {"type": "string"},
                                                        "source": {"type": "string"},
                                                        "vector_score": {"type": "number"},
                                                        "keyword_score": {"type": "number"},
                                                        "hybrid_score": {"type": "number"},
                                                        "rank": {"type": "integer"},
                                                        "metadata": {"type": "object"},
                                                    },
                                                },
                                            },
                                            "total_results": {"type": "integer"},
                                            "search_time": {"type": "number"},
                                        },
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/api/techniques": {
                "get": {
                    "summary": "List Techniques",
                    "description": "Get all available prompt techniques",
                    "responses": {
                        "200": {
                            "description": "List of techniques",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "techniques": {"type": "array", "items": {"type": "string"}},
                                            "total_count": {"type": "integer"},
                                        },
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/api/techniques/{technique_name}": {
                "get": {
                    "summary": "Get Technique Details",
                    "description": "Get detailed information about a specific technique",
                    "parameters": [
                        {
                            "name": "technique_name",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Name of the technique",
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Technique details",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "definition": {"type": "string"},
                                            "description": {"type": "string"},
                                            "examples": {"type": "array", "items": {"type": "string"}},
                                        },
                                    }
                                }
                            },
                        },
                        "404": {"description": "Technique not found"},
                    },
                }
            },
        },
        "components": {
            "schemas": {
                "PromptRequest": {
                    "type": "object",
                    "properties": {"prompt": {"type": "string"}, "technique_hint": {"type": "string"}},
                    "required": ["prompt"],
                },
                "SearchRequest": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "strategy": {"type": "string"},
                        "top_k": {"type": "integer"},
                    },
                    "required": ["query"],
                },
            }
        },
    }

    # Create documentation HTML
    docs_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced RAG API Documentation</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-bundle.css">
    <style>
        body {{
            margin: 0;
            font-family: 'Segoe UI', sans-serif;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Enhanced RAG API Documentation</h1>
        <p>Production-grade RAG application for prompt engineering</p>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="container">
        <div id="swagger-ui"></div>
    </div>
    
    <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-bundle.js"></script>
    <script>
        const spec = {json.dumps(api_docs, indent=2)};
        
        SwaggerUIBundle({{
            url: './api-spec.json',
            dom_id: '#swagger-ui',
            deepLinking: true,
            presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIBundle.presets.standalone
            ],
            plugins: [
                SwaggerUIBundle.plugins.DownloadUrl
            ],
            layout: "StandaloneLayout"
        }});
    </script>
</body>
</html>
    """

    # Save files
    build_dir = Path("build")
    build_dir.mkdir(exist_ok=True)

    # Save OpenAPI spec
    with open(build_dir / "api-spec.json", "w") as f:
        json.dump(api_docs, f, indent=2)

    # Save documentation HTML
    with open(build_dir / "api-docs.html", "w") as f:
        f.write(docs_html)


def main():
    """Generate API documentation"""
    print("Generating API documentation...")

    try:
        generate_api_docs()
        print("✅ Generated API documentation")
        print("🚀 API documentation generation complete!")

    except Exception as e:
        print(f"❌ Error generating API documentation: {e}")
        raise


if __name__ == "__main__":
    main()
