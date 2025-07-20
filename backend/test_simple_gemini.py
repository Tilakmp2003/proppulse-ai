#!/usr/bin/env python3
"""
Simple test for Gemini AI property estimation
"""
import asyncio
import os
import sys
sys.path.append('/Volumes/project/intern/proppulse-ai/backend')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

async def test_simple_gemini():
    """Simple Gemini test"""
    print("🧪 Simple Gemini Test")
    print("=" * 30)
    
    # Check environment
    gemini_key = os.getenv('GEMINI_API_KEY')
    print(f"Gemini API Key configured: {'Yes' if gemini_key else 'No'}")
    
    if not gemini_key:
        print("❌ No Gemini API key found")
        return
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        print("✅ Gemini model created successfully")
        
        # Test a simple query
        response = model.generate_content("What is 2+2?")
        print(f"✅ Simple test response: {response.text}")
        
        # Now test with our service
        from services.external_apis import ExternalAPIService
        service = ExternalAPIService()
        
        print(f"✅ Service created, Gemini available: {service.gemini_model is not None}")
        
        # Test direct Gemini estimation method
        address = "1234 Santa Monica Blvd, West Hollywood, CA 90069"
        print(f"📍 Testing Gemini estimation for: {address}")
        
        result = await service._get_gemini_property_estimation(address)
        
        if result:
            print("✅ Gemini estimation successful!")
            print(f"Property Type: {result.get('property_type')}")
            print(f"Units: {result.get('units')}")
            print(f"Estimated Value: ${result.get('estimated_value'):,}" if result.get('estimated_value') else "N/A")
        else:
            print("❌ Gemini estimation failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_gemini())
