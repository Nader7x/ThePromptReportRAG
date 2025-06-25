#!/usr/bin/env python3
"""
Test Script for Enhanced RAG API
===============================

Quick test to verify the API is working correctly.
"""

import requests
import json

API_BASE_URL = "http://localhost:8000/api"

def test_api():
    """Test the enhanced prompt API"""
    
    print("🧪 Testing Enhanced RAG API")
    print("=" * 40)
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        health = response.json()
        print(f"✅ Status: {health.get('status', 'unknown')}")
        for service, status in health.get('services', {}).items():
            print(f"   - {service}: {status}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 2: Prompt Enhancement
    print("\n2. Testing Prompt Enhancement...")
    test_prompt = "Write a story about a dragon"
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/enhance-prompt",
            json={"prompt": test_prompt},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Enhancement successful!")
            print(f"📝 Original: {result.get('original_prompt', 'N/A')}")
            print(f"✨ Enhanced: {result.get('enhanced_prompt', 'N/A')}")
            print(f"🎯 Technique: {result.get('identified_technique', 'N/A')}")
            print(f"⏱️ Time: {result.get('processing_time', 0):.2f}s")
            print(f"✅ Success: {result.get('success', False)}")
            
            # Verify the enhanced prompt is different and not empty
            enhanced = result.get('enhanced_prompt', '')
            original = result.get('original_prompt', '')
            
            if enhanced and enhanced.strip():
                if enhanced != original:
                    print("🎉 Enhancement is working properly!")
                    return True
                else:
                    print("⚠️ Enhanced prompt is the same as original")
            else:
                print("❌ Enhanced prompt is empty or missing")
                
        else:
            print(f"❌ API returned status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Enhancement test failed: {e}")
    
    return False

if __name__ == "__main__":
    success = test_api()
    if success:
        print("\n🎉 All tests passed! Streamlit should work correctly now.")
    else:
        print("\n❌ Tests failed. Check the API server.")
