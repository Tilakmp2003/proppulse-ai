#!/usr/bin/env python3
"""
Test complete property data pipeline
"""
import asyncio
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.external_apis import ExternalAPIService

async def test_complete_pipeline():
    service = ExternalAPIService()
    address = "123 Main Street Apt 5, Los Angeles, CA 90210"
    
    print(f"Testing complete pipeline for: {address}")
    print("=" * 50)
    
    try:
        result = await service.get_property_data(address)
        
        if result:
            print("✅ SUCCESS: Got property data from pipeline")
            print(f"Address: {result.get('address')}")
            print(f"Property Type: {result.get('property_type')}")
            print(f"Units: {result.get('units')}")
            print(f"Square Footage: {result.get('square_footage')}")
            print(f"Estimated Value: ${result.get('estimated_value'):,}" if result.get('estimated_value') else "No value")
            
            # Check data quality
            data_quality = result.get('data_quality', {})
            print(f"\n🔍 Data Quality:")
            print(f"  - Is Free Data: {data_quality.get('is_free_data')}")
            print(f"  - Is Estimated: {data_quality.get('is_estimated_data')}")
            print(f"  - Confidence: {data_quality.get('confidence')}%")
            print(f"  - Sources: {data_quality.get('sources')}")
            print(f"  - Notes: {data_quality.get('notes')}")
            
            # Check market data
            market_data = result.get('market_data', {})
            if market_data:
                print(f"\n💰 Market Data:")
                print(f"  - Avg Rent/Unit: ${market_data.get('avg_rent_per_unit')}")
                print(f"  - Cap Rate: {market_data.get('estimated_cap_rate')}%")
                
        else:
            print("❌ No data returned from pipeline")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_complete_pipeline())
