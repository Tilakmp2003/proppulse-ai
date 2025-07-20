import requests
import json

def test_estimation_api():
    backend_url = "https://proppulse-ai-production.up.railway.app"
    
    # Test with a multifamily address that should trigger estimation
    address = "123 Main Street Apt 5, Los Angeles, CA 90210"
    
    print(f"Testing backend estimation with: {address}")
    print("=" * 60)
    
    try:
        response = requests.post(
            f"{backend_url}/quick-analysis",
            headers={"Content-Type": "application/json"},
            json={"address": address},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ SUCCESS - Got response from backend")
            print("\nFull Response Structure:")
            print(json.dumps(data, indent=2, default=str))
            
            # Check for analysis_result
            if 'analysis_result' in data:
                analysis = data['analysis_result']
                print(f"\n🔍 Analysis Result Keys: {list(analysis.keys())}")
                
                # Check property_details
                if 'property_details' in analysis:
                    props = analysis['property_details']
                    print(f"\n🏢 Property Details:")
                    print(f"  - Type: {props.get('property_type')}")
                    print(f"  - Units: {props.get('units')}")
                    print(f"  - Square Footage: {props.get('square_footage')}")
                    print(f"  - Estimated Value: {props.get('estimated_value')}")
                
                # Check market_data
                if 'market_data' in analysis:
                    market = analysis['market_data']
                    print(f"\n💰 Market Data Keys: {list(market.keys())}")
                    
                    # Check data_quality
                    if 'data_quality' in market:
                        quality = market['data_quality']
                        print(f"\n🔍 Data Quality:")
                        print(f"  - Is Estimated: {quality.get('is_estimated_data')}")
                        print(f"  - Confidence: {quality.get('confidence')}")
                        print(f"  - Notes: {quality.get('notes')}")
                        
        else:
            print(f"\n❌ ERROR - Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")

if __name__ == "__main__":
    test_estimation_api()
