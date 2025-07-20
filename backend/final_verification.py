#!/usr/bin/env python3
"""
Final verification of the complete system
"""
import requests
import json
import time

def verify_system():
    print("🚀 FINAL SYSTEM VERIFICATION")
    print("=" * 60)
    
    # URLs for testing
    backend_url = "https://proppulse-ai-production.up.railway.app"
    frontend_url = "https://proppulse-7q5aj8h8l-tilaks-projects-d3d027be.vercel.app"
    
    # Addresses to test
    addresses = [
        "123 Main Street Apt 5, Los Angeles, CA 90210",  # Should trigger estimation
        "456 Ocean View Plaza, Santa Monica, CA 90401"    # Should show "Not available"
    ]
    
    # Wait for backend to redeploy
    print("⏳ Waiting for backend deployment (15 seconds)...")
    time.sleep(15)
    
    # Test backend health
    try:
        response = requests.get(f"{backend_url}/health", timeout=10)
        print(f"✅ Backend Health: {'OK' if response.status_code == 200 else 'ERROR'}")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Backend Health Check Failed: {e}")
    
    # Test each address
    for address in addresses:
        print(f"\n🏢 Testing address: {address}")
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
                
                # Check property details
                property_details = data.get('analysis_result', {}).get('property_details', {})
                print(f"   Property Type: {property_details.get('property_type')}")
                print(f"   Units: {property_details.get('units')}")
                print(f"   Square Footage: {property_details.get('square_footage')}")
                
                # Check data quality
                market_data = data.get('analysis_result', {}).get('market_data', {})
                data_quality = market_data.get('data_quality', {})
                
                print("\n🔍 Data Quality:")
                print(f"   Is Estimated: {data_quality.get('is_estimated_data')}")
                print(f"   Is Free Data: {data_quality.get('is_free_data')}")
                print(f"   Confidence: {data_quality.get('confidence')}%")
                print(f"   Sources: {data_quality.get('sources')}")
                if data_quality.get('notes'):
                    print(f"   Notes: {data_quality.get('notes')[:100]}...")
                    
                # Provide instructions for testing frontend
                if "Apt" in address or "Unit" in address:
                    print(f"\n🎯 Frontend Test Instructions for {address}:")
                    print(f"   1. Go to: {frontend_url}/upload?address={address.replace(' ', '%20')}")
                    print(f"   2. You should see property estimates with an Estimated Data badge")
            else:
                print(f"❌ Backend Error: {response.status_code}")
                print(f"   {response.text[:100]}...")
                
        except Exception as e:
            print(f"❌ Request Failed: {e}")
    
    print("\n✨ FINAL VERIFICATION COMPLETE")
    print("=" * 60)
    print(f"➡️ Visit frontend: {frontend_url}")
    print("1. Enter address: 123 Main Street Apt 5, Los Angeles, CA 90210")
    print("2. Should see property estimates with 'Estimated Data' badge")
    print("3. Test non-apartment address to see 'Not available'")
            
if __name__ == "__main__":
    verify_system()
