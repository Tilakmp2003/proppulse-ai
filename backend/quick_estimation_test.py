#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.external_apis import ExternalAPIService

async def quick_test():
    service = ExternalAPIService()
    address = "123 Main Street Apt 5, Los Angeles, CA 90210"
    print(f"Testing smart estimation for: {address}")
    
    try:
        result = await service.get_property_data(address)
        print(f"✅ Property Type: {result.get('property_type', 'None')}")
        print(f"✅ Units: {result.get('units', 'None')}")
        print(f"✅ Estimated Value: ${result.get('estimated_value', 'None'):,}" if result.get('estimated_value') else "✅ Estimated Value: None")
        print(f"✅ Data Quality - Is Estimated: {result.get('data_quality', {}).get('is_estimated_data', 'None')}")
        print(f"✅ Data Quality - Confidence: {result.get('data_quality', {}).get('confidence', 'None')}%")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(quick_test())
