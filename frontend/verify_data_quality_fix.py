import requests
import json
import time

def verify_data_quality_fix():
    backend_url = "https://proppulse-ai-production.up.railway.app"
    
    # Test with a multifamily address that should trigger estimation
    address = "123 Main Street Apt 5, Los Angeles, CA 90210"
    
    print(f"Testing backend data quality fix with: {address}")
    print("=" * 60)
    
    # Wait for Railway deployment to complete (typically takes 1-2 minutes)
    print("Waiting 30 seconds for Railway deployment to complete...")
    time.sleep(30)
    
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
            
            # Check for market_data and data_quality
            if 'analysis_result' in data and 'market_data' in data['analysis_result']:
                market = data['analysis_result']['market_data']
                
                if 'data_quality' in market:
                    quality = market['data_quality']
                    print(f"\n🔍 Data Quality (Fixed):")
                    print(f"  - Is Estimated: {quality.get('is_estimated_data')}")
                    print(f"  - Confidence: {quality.get('confidence')}")
                    print(f"  - Sources: {quality.get('sources')}")
                    print(f"  - Notes: {quality.get('notes')}")
                    
                    # Validation
                    if quality.get('is_estimated_data') is not None:
                        print("\n✅ FIX VERIFIED - Data quality information is properly included!")
                    else:
                        print("\n⚠️ ISSUE PERSISTS - Data quality still has None values")
                else:
                    print("\n⚠️ data_quality field still missing from market_data")
            else:
                print("\n⚠️ Required fields missing from response")
                
            # Print full response structure for debugging
            print("\nFull Response Structure:")
            print(json.dumps(data, indent=2, default=str))
            
        else:
            print(f"\n❌ ERROR - Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")

if __name__ == "__main__":
    verify_data_quality_fix()
