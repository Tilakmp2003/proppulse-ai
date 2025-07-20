#!/usr/bin/env python3
"""
Test the updated external API service
"""
import asyncio
import sys
import os
sys.path.insert(0, '/Volumes/project/intern/proppulse-ai/backend')

from services.external_apis import ExternalAPIService

async def test_external_api():
    print("🔍 Testing Updated External API Service")
    print("=" * 50)
    
    service = ExternalAPIService()
    
    test_address = "16633 Ventura Blvd, Encino, CA 91436"
    print(f"Testing address: {test_address}")
    
    try:
        result = await service.get_property_data(test_address)
        print(f"\n✅ Results:")
        print(f"Property Type: {result.get('property_type')}")
        print(f"Units: {result.get('units')}")
        print(f"Square Footage: {result.get('square_footage')}")
        
        data_quality = result.get('data_quality', {})
        print(f"Data Quality Notes: {data_quality.get('notes')}")
        print(f"Confidence: {data_quality.get('confidence')}")
        print(f"Sources: {data_quality.get('sources')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_external_api())
