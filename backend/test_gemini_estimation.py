#!/usr/bin/env python3
"""
Test Gemini AI property estimation functionality
"""
import asyncio
import os
import sys
sys.path.append('/Volumes/project/intern/proppulse-ai/backend')

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from services.external_apis import ExternalAPIService

async def test_gemini_estimation():
    """Test Gemini AI property estimation"""
    print("🧪 Testing Gemini AI Property Estimation")
    print("=" * 50)
    
    # Test address
    address = "1234 Santa Monica Blvd, West Hollywood, CA 90069"
    
    # Initialize service
    service = ExternalAPIService()
    
    # Check if Gemini is configured
    if not service.gemini_model:
        print("❌ Gemini AI not configured (GEMINI_API_KEY missing)")
        return
    
    print(f"✅ Gemini AI configured: {service.gemini_model}")
    print(f"📍 Testing address: {address}")
    print()
    
    try:
        # Get property data (should use Gemini if ATTOM not available)
        property_data = await service.get_property_data(address)
        
        print("📊 Property Data Result:")
        print("-" * 30)
        
        # Check what we got
        data_quality = property_data.get("data_quality", {})
        sources = data_quality.get("sources", [])
        confidence = data_quality.get("confidence", 0)
        
        print(f"Property Type: {property_data.get('property_type', 'N/A')}")
        print(f"Units: {property_data.get('units', 'N/A')}")
        print(f"Square Footage: {property_data.get('square_footage', 'N/A')}")
        print(f"Year Built: {property_data.get('year_built', 'N/A')}")
        print(f"Estimated Value: ${property_data.get('estimated_value', 'N/A'):,}" if property_data.get('estimated_value') else "Estimated Value: N/A")
        print()
        print(f"📈 Data Quality:")
        print(f"  Sources: {sources}")
        print(f"  Confidence: {confidence}%")
        print(f"  Is Estimated: {data_quality.get('is_estimated_data', False)}")
        print(f"  Notes: {data_quality.get('notes', 'N/A')}")
        
        # Check if Gemini was used
        if "Gemini" in str(sources):
            print("\n✅ SUCCESS: Gemini AI provided property estimates!")
            
            # Show additional Gemini data
            market_data = property_data.get('market_data', {})
            neighborhood_info = property_data.get('neighborhood_info', {})
            
            if market_data:
                print(f"\n💰 Market Data:")
                print(f"  Avg Rent/Unit: ${market_data.get('avg_rent_per_unit', 'N/A')}")
                print(f"  Est Cap Rate: {market_data.get('estimated_cap_rate', 'N/A')}%")
                print(f"  Price/SqFt: ${market_data.get('price_per_sqft', 'N/A')}")
            
            if neighborhood_info:
                print(f"\n🏘️ Neighborhood Info:")
                print(f"  Description: {neighborhood_info.get('area_description', 'N/A')}")
                print(f"  Walk Score: {neighborhood_info.get('estimated_walk_score', 'N/A')}")
        else:
            print(f"\n⚠️ Gemini AI was not used. Sources: {sources}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gemini_estimation())
