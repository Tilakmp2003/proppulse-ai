import requests
import json
import sys

def test_address(address):
    print(f"\nTesting address: {address}")
    try:
        response = requests.post(
            "https://proppulse-ai-production.up.railway.app/quick-analysis",
            headers={"Content-Type": "application/json"},
            json={"address": address},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            property_details = data.get("analysis_result", {}).get("property_details", {})
            market_data = data.get("analysis_result", {}).get("market_data", {})
            data_quality = market_data.get("data_quality", {})
            
            print(f"Property Type: {property_details.get('property_type', 'Not available')}")
            print(f"Units: {property_details.get('units', 'Not available')}")
            print(f"Square Footage: {property_details.get('square_footage', 'Not available')}")
            print(f"Market Value: ${property_details.get('market_value', 'Not available')}")
            print(f"Data Quality: {'Estimated' if data_quality.get('is_estimated_data') else 'Real'} data")
            print(f"Notes: {data_quality.get('notes', 'Not available')}")
            return True
        else:
            print(f"Error: Status code {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

# Try different property types
addresses = [
    "123 Main St, Anytown USA",  # Single family
    "123 Office Plaza, Business District",  # Commercial
    "Wilshire Apartment Complex, Los Angeles, CA"  # Multifamily
]

success = 0
for address in addresses:
    if test_address(address):
        success += 1

print(f"\nSuccessful tests: {success}/{len(addresses)}")
if success == len(addresses):
    print("✅ All tests passed! The fix is working correctly.")
else:
    print("❌ Some tests failed. The fix may not be completely deployed yet.")
