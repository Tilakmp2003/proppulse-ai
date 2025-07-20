import requests
import json
from time import sleep

def test_backend_estimation():
    """Test the backend estimation for different property types"""
    backend_url = "https://proppulse-ai-production.up.railway.app"
    print(f"Testing backend at {backend_url}...")
    
    # Test different address types
    addresses = [
        # Single family homes
        "123 Main St, Austin, TX 78701",
        "456 Residential Lane, San Francisco, CA 94105",
        
        # Commercial properties
        "789 Office Plaza, Dallas, TX 75201",
        "101 Business Center, Chicago, IL 60601",
        
        # Multifamily properties
        "Wilshire Apartment Complex, Los Angeles, CA 90036",
        "567 Tower Apartments Unit 301, New York, NY 10001"
    ]
    
    results = {}
    
    for address in addresses:
        print(f"\nTesting address: {address}")
        try:
            response = requests.post(
                f"{backend_url}/quick-analysis",
                json={"address": address},
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ Error {response.status_code}: {response.text}")
                results[address] = {"status": "error", "code": response.status_code}
                continue
                
            data = response.json()
            property_details = data.get("analysis_result", {}).get("property_details", {})
            market_data = data.get("analysis_result", {}).get("market_data", {})
            data_quality = market_data.get("data_quality", {})
            
            # Print key information
            print(f"✅ Property Type: {property_details.get('property_type', 'Not available')}")
            print(f"   Units: {property_details.get('units', 'Not available')}")
            print(f"   Square Footage: {property_details.get('square_footage', 'Not available')}")
            print(f"   Market Value: ${property_details.get('market_value', 'Not available')}")
            print(f"   Data Quality: {'Estimated' if data_quality.get('is_estimated_data') else 'Real'} data")
            
            # Store results
            results[address] = {
                "status": "success",
                "property_type": property_details.get("property_type"),
                "units": property_details.get("units"),
                "has_meaningful_data": bool(property_details.get("property_type") != "Unknown" and property_details.get("units")),
                "is_estimated": bool(data_quality.get("is_estimated_data"))
            }
            
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            results[address] = {"status": "exception", "message": str(e)}
        
        sleep(1)  # Be nice to the API
    
    # Summary
    print("\n=== SUMMARY ===")
    success_count = sum(1 for r in results.values() if r.get("status") == "success")
    estimation_count = sum(1 for r in results.values() if r.get("is_estimated"))
    print(f"Total addresses tested: {len(addresses)}")
    print(f"Successful responses: {success_count}")
    print(f"Addresses with estimation: {estimation_count}")
    
    all_have_data = all(r.get("has_meaningful_data", False) for r in results.values() if r.get("status") == "success")
    print(f"\nAll addresses have meaningful data: {'✅ YES' if all_have_data else '❌ NO'}")
    
    if not all_have_data:
        print("\nAddresses missing data:")
        for addr, result in results.items():
            if result.get("status") == "success" and not result.get("has_meaningful_data"):
                print(f"- {addr}")
    
    return results

if __name__ == "__main__":
    results = test_backend_estimation()
