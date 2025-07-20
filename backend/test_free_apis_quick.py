#!/usr/bin/env python3
"""
Quick test for free property data APIs
"""
import asyncio
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.free_property_apis import FreePropertyDataService

async def test_free_apis():
    service = FreePropertyDataService()
    address = "123 Main Street, Los Angeles, CA 90210"
    
    print(f"Testing free APIs for: {address}")
    print("=" * 50)
    
    # Try each API separately for better debugging
    print("\n🔍 Testing OpenStreetMap API...")
    try:
        osm_data = await service.get_openstreetmap_data(address)
        print(f"OpenStreetMap result: {'✅ Success' if osm_data else '❌ Failed'}")
        if osm_data:
            print(f"  - Coordinates: {osm_data.get('latitude')}, {osm_data.get('longitude')}")
            print(f"  - Display name: {osm_data.get('display_name')}")
    except Exception as e:
        print(f"OpenStreetMap error: {str(e)}")

    print("\n🔍 Testing US Census API...")
    try:
        census_data = await service.get_census_data(address)
        print(f"Census API result: {'✅ Success' if census_data else '❌ Failed'}")
        if census_data:
            print(f"  - Census data keys: {list(census_data.keys())}")
    except Exception as e:
        print(f"Census API error: {str(e)}")
    
    print("\n🔍 Testing comprehensive free data...")
    try:
        result = await service.get_comprehensive_free_data(address)
        
        if result and not result.get('error'):
            print("✅ SUCCESS: Got data from free APIs")
            print(f"Property type: {result.get('property_type', 'Not found')}")
            print(f"Units: {result.get('units', 'Not found')}")
            print(f"Square footage: {result.get('square_footage', 'Not found')}")
            
            market_data = result.get('market_data', {})
            print(f"Estimated value: {market_data.get('estimated_property_value', 'Not found')}")
            print(f"Estimated rent: {market_data.get('estimated_rent_per_unit', 'Not found')}")
            
            # Check data sources
            sources = result.get('data_sources', {})
            print(f"\nData sources used: {list(sources.keys())}")
            
            # Print full data structure for debugging
            print("\n🔍 FULL DATA STRUCTURE:")
            print(json.dumps(result, indent=2, default=str))
            
        else:
            print("❌ FAILED: Free APIs returned no data or error")
            if result and result.get('error'):
                print(f"Error: {result['error']}")
            else:
                print("No error message provided, returned data was:", result)
    
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_free_apis())
