#!/usr/bin/env python3
"""
Test ATTOM API integration and verify real data vs estimates
"""
import requests
import json

def test_attom_integration():
    """Test if ATTOM API is working and returning real data"""
    print("🔍 Testing ATTOM API Integration")
    print("=" * 50)
    
    # Test addresses
    test_addresses = [
        "5325 Newcastle Ave UNIT 319, Encino, CA 91316",
        "5678 Wilshire Blvd, Los Angeles, CA 90036"
    ]
    
    backend_url = "https://proppulse-ai-production.up.railway.app"
    
    for address in test_addresses:
        print(f"\n🏠 Testing: {address}")
        print("-" * 40)
        
        try:
            # Test the quick-analysis endpoint
            response = requests.post(
                f"{backend_url}/quick-analysis",
                json={"address": address},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response received")
                
                # Check data quality
                data_quality = data.get("data_quality", {})
                confidence = data_quality.get("confidence", 0)
                sources = data_quality.get("sources", [])
                notes = data_quality.get("notes", "")
                is_estimated = data_quality.get("is_estimated_data", True)
                
                print(f"🎯 Property Type: {data.get('property_type', 'N/A')}")
                print(f"🏠 Units: {data.get('units', 'N/A')}")
                print(f"📐 Square Footage: {data.get('square_footage', 'N/A')}")
                print(f"📊 Confidence: {confidence}%")
                print(f"🔍 Sources: {sources}")
                print(f"📝 Notes: {notes}")
                print(f"⚡ Is Estimated: {is_estimated}")
                
                # Check if ATTOM data is present
                if "attom" in sources or "ATTOM" in str(sources):
                    print("✅ ATTOM DATA FOUND - Real property records!")
                else:
                    print("⚠️  NO ATTOM DATA - Using estimates/public data only")
                    
                # Check if this is real data or estimates
                if confidence >= 90:
                    print("🎯 HIGH CONFIDENCE - Likely real property data")
                elif confidence >= 60:
                    print("📊 MEDIUM CONFIDENCE - Public data with some estimates")
                else:
                    print("❌ LOW CONFIDENCE - No real data available")
                    
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n💡 RECOMMENDATION:")
    print(f"If you see 'NO ATTOM DATA' above, add ATTOM_API_KEY to Railway environment variables")
    print(f"This will provide real property records instead of estimates")

if __name__ == "__main__":
    test_attom_integration()
