#!/usr/bin/env python3
"""
Quick integration test for API and Streamlit
"""
import requests
import json

def test_api():
    """Test the API endpoint"""
    print("🧪 Testing API Integration")
    print("-" * 40)
    
    try:
        # Test health endpoint first
        print("1. Testing health endpoint...")
        health_response = requests.get('http://localhost:8000/api/health', timeout=10)
        print(f"   Health Status: {health_response.status_code}")
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   System Status: {health_data.get('status')}")
            
            # Test enhancement endpoint
            print("\n2. Testing enhancement endpoint...")
            prompt_data = {'prompt': 'Write a summary about machine learning'}
            enhance_response = requests.post('http://localhost:8000/api/enhance-prompt', 
                                           json=prompt_data, timeout=30)
            print(f"   Enhancement Status: {enhance_response.status_code}")
            
            if enhance_response.status_code == 200:
                data = enhance_response.json()
                print(f"   Success: {data.get('success')}")
                print(f"   Technique: {data.get('identified_technique')}")
                print(f"   Original: {data.get('original_prompt')}")
                
                enhanced = data.get('enhanced_prompt', '')
                print(f"\n   Enhanced Prompt ({len(enhanced)} chars):")
                print("   " + "=" * 50)
                # Print first 200 chars to see what we got
                print(f"   {enhanced[:200]}{'...' if len(enhanced) > 200 else ''}")
                print("   " + "=" * 50)
                
                # Analysis
                if data.get('success') and enhanced and len(enhanced) > 10:
                    print("\n   ✅ API Enhancement: WORKING")
                    return True
                else:
                    print("\n   ❌ API Enhancement: FAILED")
                    return False
            else:
                print(f"   Enhancement failed: {enhance_response.text}")
                return False
        else:
            print(f"   Health check failed: {health_response.text}")
            return False
            
    except Exception as e:
        print(f"   API Test Error: {e}")
        return False

def test_streamlit_connection():
    """Test if Streamlit is accessible"""
    print("\n🌐 Testing Streamlit Connection")
    print("-" * 40)
    
    try:
        response = requests.get('http://localhost:8501', timeout=5)
        if response.status_code == 200:
            print("   ✅ Streamlit: ACCESSIBLE")
            return True
        else:
            print(f"   ❌ Streamlit: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Streamlit: {e}")
        return False

if __name__ == "__main__":
    print("🚀 RAG Integration Test")
    print("=" * 50)
    
    api_ok = test_api()
    streamlit_ok = test_streamlit_connection()
    
    print("\n📊 SUMMARY")
    print("-" * 20)
    print(f"API: {'✅ Working' if api_ok else '❌ Failed'}")
    print(f"Streamlit: {'✅ Working' if streamlit_ok else '❌ Failed'}")
    
    if api_ok and streamlit_ok:
        print("\n🎉 Integration test PASSED!")
        print("Both API and Streamlit are working. Check the Streamlit UI manually.")
    else:
        print("\n⚠️ Integration test FAILED!")
        print("Check the individual component errors above.")
