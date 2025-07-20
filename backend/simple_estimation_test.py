#!/usr/bin/env python3
"""
Simple test for smart estimation logic
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.external_apis import ExternalAPIService

def test_estimation_logic():
    service = ExternalAPIService()
    
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
        
        # Test the estimation function directly
        result = service._get_basic_property_estimates(address)
        
        if result:
            print("✅ Got estimation!")
            print(f"Property Type: {result.get('property_type')}")
            print(f"Units: {result.get('units')}")
            print(f"Square Footage: {result.get('square_footage')}")
            print(f"Estimated Value: ${result.get('estimated_value'):,}" if result.get('estimated_value') else "No value")
            
            # Check data quality
            data_quality = result.get('data_quality', {})
            print(f"Is Estimated: {data_quality.get('is_estimated_data')}")
            print(f"Confidence: {data_quality.get('confidence')}%")
            print(f"Notes: {data_quality.get('notes')}")
        else:
            print("❌ No estimation (probably not multifamily)")

if __name__ == "__main__":
    test_estimation_logic()
