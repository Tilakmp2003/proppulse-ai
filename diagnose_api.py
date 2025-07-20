import requests
import json
import time

def test_address(address):
    """Test the PropPulse API with a given address"""
    print(f"\nTesting address: {address}")
    try:
        response = requests.post(
            "https://proppulse-ai-production.up.railway.app/quick-analysis",
            headers={"Content-Type": "application/json"},
            json={"address": address},
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"Error: {response.status_code}, {response.text}")
            return
        
        data = response.json()
        print("Full API response:")
        print(json.dumps(data, indent=2))
        
        property_details = data.get("analysis_result", {}).get("property_details", {})
        market_data = data.get("analysis_result", {}).get("market_data", {})
        data_quality = market_data.get("data_quality", {})
        
        print("\nExtracted property details:")
        print(f"Property Type: {property_details.get('property_type', 'Not available')}")
        print(f"Units: {property_details.get('units', 'Not available')}")
        print(f"Square Footage: {property_details.get('square_footage', 'Not available')}")
        print(f"Market Value: ${property_details.get('market_value', 'Not available')}")
        print(f"Data Quality: {'Estimated' if data_quality.get('is_estimated_data') else 'Real'} data")
        print(f"Notes: {data_quality.get('notes', 'Not available')}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

# Test with the Wilshire address from your logs
wilshire_address = "5678, Wilshire Boulevard, Miracle Mile, Mid-Wilshire, Los Angeles, Los Angeles County, California, 90036, United States"
test_address(wilshire_address)

# Also test a simple single-family address
test_address("123 Main St, Anytown USA")

print("\nChecking if the API is returning data in the expected format...")
print("If you see 'Unknown' for property type or 0 for units, the fix may not be deployed yet.")
print("If you see actual property details and 'Estimated' data quality, the fix is working!")
