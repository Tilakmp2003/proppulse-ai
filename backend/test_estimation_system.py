#!/usr/bin/env python3
"""
Test the smart property estimation system
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.external_apis import ExternalAPIService

async def test_estimation_system():
    service = ExternalAPIService()
    
    # Test addresses with different patterns
    test_addresses = [
        "123 Main Street Apt 5, Los Angeles, CA 90210",
        "456 Ocean View Complex Unit 22, Santa Monica, CA 90401", 
        "789 Sunset Towers #15, Hollywood, CA 90028",
        "321 Park Place, Beverly Hills, CA 90210"  # No unit indicators
    ]
    
    for address in test_addresses:
        print(f"\n{'='*60}")
        print(f"Testing: {address}")
        print('='*60)
        
        try:
            result = await service.get_property_data(address)
            
            if result:
                print(f"✅ Got property data!")
                print(f"Address: {result.get('address', 'Not found')}")
                print(f"Property Type: {result.get('property_type', 'Not found')}")
                print(f"Units: {result.get('units', 'Not found')}")
                print(f"Square Footage: {result.get('square_footage', 'Not found')}")
                print(f"Estimated Value: ${result.get('estimated_value', 'Not found'):,}" if result.get('estimated_value') else "Estimated Value: Not found")
                
                # Check data quality
                data_quality = result.get('data_quality', {})
                if data_quality.get('is_estimated_data'):
                    print(f"🔍 Data Quality: ESTIMATED (Confidence: {data_quality.get('confidence', 0)}%)")
                    print(f"📝 Notes: {data_quality.get('notes', 'No notes')}")
                elif data_quality.get('is_free_data'):
                    print(f"🔍 Data Quality: REAL DATA from free sources")
                else:
                    print(f"🔍 Data Quality: {data_quality}")
                    
            else:
                print("❌ No data returned")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_estimation_system())
