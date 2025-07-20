#!/usr/bin/env python3
"""
Quick test script to verify ATTOM Data API integration
"""
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.free_property_apis import FreePropertyDataService

async def test_attom_integration():
    """Test ATTOM API integration"""
    print("🔍 Testing ATTOM Data API Integration")
    print("=" * 50)
    
    service = FreePropertyDataService()
    
    # Check if ATTOM API key is configured
    if service.attom_api_key:
        print(f"✅ ATTOM API Key configured: {service.attom_api_key[:10]}...")
    else:
        print("⚠️  ATTOM API Key not configured - will use free data sources only")
    
    # Test addresses
    test_addresses = [
        "16633 Ventura Blvd, Encino, CA 91436",
        "1234 Sunset Blvd, Los Angeles, CA 90028",
        "123 Main St, Austin, TX 78701"
    ]
    
    for address in test_addresses:
        print(f"\n🏠 Testing: {address}")
        print("-" * 40)
        
        try:
            # Get comprehensive data
            data = await service.get_comprehensive_free_data(address)
            
            if "error" in data:
                print(f"❌ Error: {data['error']}")
                continue
            
            # Display results
            print(f"📍 Property Type: {data.get('property_type', 'Unknown')}")
            print(f"🏠 Units: {data.get('units', 'N/A')}")
            print(f"📐 Square Footage: {data.get('square_footage', 'N/A')}")
            print(f"📅 Year Built: {data.get('year_built', 'N/A')}")
            
            # Check if ATTOM data was used
            attom_data = data.get('data_sources', {}).get('attom', {})
            if attom_data:
                print(f"✅ ATTOM Data: Found property details")
                if 'assessed_value' in data:
                    print(f"💰 Assessed Value: ${data['assessed_value']:,}")
            else:
                print(f"📊 Using inferred data from free sources")
            
            # Market estimates
            market_data = data.get('market_data', {})
            if market_data:
                rent = market_data.get('estimated_rent_per_unit', 0)
                value = market_data.get('estimated_property_value', 0)
                print(f"🏠 Estimated Rent: ${rent:,}/month")
                print(f"🏢 Estimated Value: ${value:,}")
            
            print(f"📋 Data Quality: {data.get('data_quality', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ Error testing {address}: {e}")
    
    print("\n✅ ATTOM Integration Test Complete")

if __name__ == "__main__":
    asyncio.run(test_attom_integration())
