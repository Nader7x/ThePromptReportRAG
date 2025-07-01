#!/usr/bin/env python3
"""Quick test of the enhanced prompt system"""

import os
from EnhancedPrompt import create_production_rag

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-api-key")

def test_single_prompt():
    print("Testing single prompt...")
    rag = create_production_rag(GEMINI_API_KEY)
    
    result = rag.process_prompt("Write a summary about machine learning")
    
    print(f"✅ Success: {result['success']}")
    print(f"🔍 Technique: {result['identified_technique']}")
    print(f"📝 Enhanced: {result['enhanced_prompt']}")
    
if __name__ == "__main__":
    test_single_prompt()
