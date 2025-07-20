import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote

# List of addresses to test
addresses = [
    # Multifamily addresses (should trigger estimation)
    "123 Main Street Apt 5, Los Angeles, CA 90210",
    "456 Park Avenue Unit 301, New York, NY 10022",
    "789 Pine Street #42, Chicago, IL 60601",
    "Sunset Towers Apt 12B, Miami, FL 33131",
    
    # Commercial properties
    "555 Office Park Drive, Houston, TX 77002",
    "Gateway Business Plaza, 1200 Commerce St, Dallas, TX 75202",
    
    # Single-family homes
    "7825 Sunset Boulevard, Los Angeles, CA 90046",
    "425 Oak Street, Portland, OR 97204"
]

def test_address(address):
    backend_url = "https://proppulse-ai-production.up.railway.app"
    
    print(f"\n\n🏢 Testing address: {address}")
    print("=" * 60)
    
    try:
        response = requests.post(
            f"{backend_url}/quick-analysis",
            headers={"Content-Type": "application/json"},
            json={"address": address},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Got response from backend")
            
            # Extract key information
            property_details = data.get('analysis_result', {}).get('property_details', {})
            market_data = data.get('analysis_result', {}).get('market_data', {})
            data_quality = market_data.get('data_quality', {})
            
            # Display property information
            print(f"   Property Type: {property_details.get('property_type', 'None')}")
            print(f"   Units: {property_details.get('units', 'None')}")
            print(f"   Square Footage: {property_details.get('square_footage', 'None')}")
            
            # Display data quality information
            print(f"\n🔍 Data Quality:")
            print(f"   Is Estimated: {data_quality.get('is_estimated_data')}")
            print(f"   Is Free Data: {data_quality.get('is_free_data')}")
            print(f"   Confidence: {data_quality.get('confidence')}%")
            print(f"   Sources: {data_quality.get('sources')}")
            
            # Generate frontend URL for testing
            encoded_address = quote(address)
            frontend_url = f"https://proppulse-7q5aj8h8l-tilaks-projects-d3d027be.vercel.app/upload?address={encoded_address}"
            print(f"\n🌐 Frontend Test URL: {frontend_url}")
            
            return True
        else:
            print(f"❌ Error - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

# Test each address
print("🚀 Testing multiple property addresses")
print("=" * 80)

# Use ThreadPoolExecutor to test multiple addresses in parallel
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(test_address, addresses))

# Summary
success_count = results.count(True)
print("\n" + "=" * 80)
print(f"✨ TESTING COMPLETE: {success_count}/{len(addresses)} addresses successfully processed")
