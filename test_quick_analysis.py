"""
Quick API test script to debug property data issues
"""
import requests
import json
import sys

def test_quick_analysis(address):
    """Test the quick-analysis endpoint"""
    print(f"Testing quick-analysis endpoint with address: {address}")
    
    try:
        url = "http://localhost:8000/quick-analysis"
        headers = {"Content-Type": "application/json"}
        payload = {"address": address}
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print("Success! Response:")
            print(json.dumps(data, indent=2))
            
            # Check the neighborhood info/data paths
            print("\nNeighborhood info check:")
            if "analysis_result" in data and "neighborhood_info" in data["analysis_result"]:
                print(f"neighborhood_info: {data['analysis_result']['neighborhood_info']}")
            else:
                print("neighborhood_info not found in response")
                
            if "analysis_result" in data and "neighborhood_data" in data["analysis_result"]:
                print(f"neighborhood_data: {data['analysis_result']['neighborhood_data']}")
            else:
                print("neighborhood_data not found in response")
                
        else:
            print(f"Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    address = "1234 Commerce St, Austin, TX 78701"
    if len(sys.argv) > 1:
        address = sys.argv[1]
        
    test_quick_analysis(address)
