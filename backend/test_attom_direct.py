#!/usr/bin/env python3
"""
Test ATTOM API directly
"""
import asyncio
import os
import sys
import requests
sys.path.append('/Volumes/project/intern/proppulse-ai/backend')

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

def test_attom_api_direct():
    """Test ATTOM API directly"""
    print("🧪 Testing ATTOM API Direct Access")
    print("=" * 50)
    
    api_key = os.getenv('ATTOM_API_KEY')
    if not api_key:
        print("❌ ATTOM API Key not found")
        return
    
    print(f"✅ ATTOM API Key: {api_key[:20]}...")
    
    # Test ATTOM API endpoint
    address = "1234 Santa Monica Blvd, West Hollywood, CA 90069"
    
    # ATTOM Property Detail API
    url = "https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/detail"
    
    headers = {
        "Accept": "application/json",
        "apikey": api_key
    }
    
    params = {
        "address1": address,
        "format": "json"
    }
    
    print(f"📍 Testing address: {address}")
    print(f"🌐 API URL: {url}")
    print(f"📋 Params: {params}")
    print()
    
    try:
        print("📡 Making API request...")
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS: ATTOM API Response Received!")
            print(f"📝 Response: {data}")
            
            # Check if we have property data
            if "property" in data:
                properties = data["property"]
                if properties:
                    prop = properties[0]
                    print(f"\n🏠 Property Details:")
                    print(f"  Address: {prop.get('address', {}).get('oneLine', 'N/A')}")
                    print(f"  Property Type: {prop.get('summary', {}).get('proptype', 'N/A')}")
                    print(f"  Year Built: {prop.get('summary', {}).get('yearbuilt', 'N/A')}")
                    print(f"  Living Area: {prop.get('building', {}).get('size', {}).get('livingsize', 'N/A')} sq ft")
                    print(f"  Bedrooms: {prop.get('building', {}).get('rooms', {}).get('beds', 'N/A')}")
                    print(f"  Bathrooms: {prop.get('building', {}).get('rooms', {}).get('bathstotal', 'N/A')}")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_attom_api_direct()
