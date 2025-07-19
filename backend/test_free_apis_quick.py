#!/usr/bin/env python3
"""
Quick test for free property data APIs
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.free_property_apis import FreePropertyDataService

async def test_free_apis():
    service = FreePropertyDataService()
    address = "123 Main Street, Los Angeles, CA 90210"
    
    print(f"Testing free APIs for: {address}")
    print("=" * 50)
    
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
            
        else:
            print("❌ FAILED: Free APIs returned no data or error")
            if result and result.get('error'):
                print(f"Error: {result['error']}")
    
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_free_apis())
