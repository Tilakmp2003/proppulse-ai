#!/usr/bin/env python3
"""
Direct test of estimation logic
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.external_apis import ExternalAPIService

def test_direct_estimation():
    service = ExternalAPIService()
    
    # Test addresses
    addresses = [
        "123 Main Street Apt 5, Los Angeles, CA 90210",
        "456 Ocean View Complex Unit 22, Santa Monica, CA 90401"
    ]
    
    for address in addresses:
        print(f"\nTesting direct estimation for: {address}")
        print("=" * 60)
        
        # Test direct call to the estimation function
        result = service._get_basic_property_estimates(address)
        
        if result:
            print("✅ ESTIMATION SUCCEEDED!")
            print(f"Property Type: {result.get('property_type')}")
            print(f"Units: {result.get('units')}")
            print(f"Square Footage: {result.get('square_footage')}")
            print(f"Estimated Value: ${result.get('estimated_value'):,}" if result.get('estimated_value') else "No value estimate")
            
            # Check data quality
            data_quality = result.get('data_quality', {})
            print(f"\nData Quality:")
            print(f"Is Estimated: {data_quality.get('is_estimated_data')}")
            print(f"Confidence: {data_quality.get('confidence')}%")
            print(f"Notes: {data_quality.get('notes')}")
        else:
            print("❌ ESTIMATION FAILED")
            print("No estimation data returned")
        
if __name__ == "__main__":
    test_direct_estimation()
