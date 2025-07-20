import requests
import json

def test_quick_analysis():
    backend_url = "https://proppulse-ai-production.up.railway.app"
    
    # Test with a multifamily address that should trigger estimation
    address = "123 Main Street Apt 5, Los Angeles, CA 90210"
    
    print(f"Testing quick analysis with: {address}")
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
            
            # Look specifically for data_quality in the response
            if 'analysis_result' in data and 'market_data' in data['analysis_result']:
                market_data = data['analysis_result']['market_data']
                print(f"\n🔍 Market Data Structure:")
                for key in market_data:
                    print(f"  - {key}")
                
                if 'data_quality' in market_data:
                    data_quality = market_data['data_quality']
                    print(f"\n📊 Data Quality Field Values:")
                    print(json.dumps(data_quality, indent=2))
                else:
                    print("\n❌ data_quality field missing in market_data")
            else:
                print("\n❌ Required fields missing in response")
                
        else:
            print(f"\n❌ ERROR - Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")

if __name__ == "__main__":
    test_quick_analysis()
