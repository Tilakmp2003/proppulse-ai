#!/usr/bin/env python3
"""
Test backend endpoints directly
"""
import requests
import json

def test_backend():
    base_url = "https://proppulse-ai-production.up.railway.app"
    
    print("Testing backend endpoints...")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"Health endpoint: {'✅ OK' if response.status_code == 200 else '❌ Failed'}")
        if response.status_code == 200:
            print(f"  Response: {response.json()}")
    except Exception as e:
        print(f"Health endpoint error: {e}")
    
    # Test quick-analysis endpoint
    try:
        address = "123 Main Street Apt 5, Los Angeles, CA 90210"
        payload = {"address": address}
        
        print(f"\nTesting quick-analysis with: {address}")
        response = requests.post(
            f"{base_url}/quick-analysis",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        print(f"Quick-analysis endpoint: {'✅ OK' if response.status_code == 200 else '❌ Failed'}")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            
            # Check if we have analysis_result
            if 'analysis_result' in data:
                analysis = data['analysis_result']
                print(f"Analysis result keys: {list(analysis.keys())}")
                
                if 'property_details' in analysis:
                    props = analysis['property_details']
                    print(f"Property details: {props}")
                
                if 'market_data' in analysis:
                    market = analysis['market_data']
                    print(f"Market data keys: {list(market.keys())}")
                    
                    # Check data quality
                    if 'data_quality' in market:
                        quality = market['data_quality']
                        print(f"Data quality: {quality}")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Quick-analysis error: {e}")

if __name__ == "__main__":
    test_backend()
