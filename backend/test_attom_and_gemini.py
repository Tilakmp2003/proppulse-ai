#!/usr/bin/env python3
"""
Test ATTOM API + Gemini AI Integration
"""
import asyncio
import os
import sys
sys.path.append('/Volumes/project/intern/proppulse-ai/backend')

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from services.external_apis import ExternalAPIService

async def test_attom_and_gemini():
    """Test ATTOM API and Gemini AI integration"""
    print("🧪 Testing ATTOM API + Gemini AI Integration")
    print("=" * 60)
    
    # Test addresses
    addresses = [
        "1234 Santa Monica Blvd, West Hollywood, CA 90069",
        "123 Main Street, Los Angeles, CA 90210",
        "456 Oak Avenue, Beverly Hills, CA 90210"
    ]
    
    # Initialize service
    service = ExternalAPIService()
    
    # Check configurations
    print("🔧 Configuration Check:")
    print(f"  ATTOM API Key: {'✅ Set' if os.getenv('ATTOM_API_KEY') else '❌ Missing'}")
    print(f"  Gemini AI: {'✅ Configured' if service.gemini_model else '❌ Missing'}")
    print()
    
    for i, address in enumerate(addresses, 1):
        print(f"📍 Test {i}: {address}")
        print("-" * 50)
        
        try:
            # Get property data
            property_data = await service.get_property_data(address)
            
            # Check what we got
            data_quality = property_data.get("data_quality", {})
            sources = data_quality.get("sources", [])
            confidence = data_quality.get("confidence", 0)
            is_estimated = data_quality.get("is_estimated_data", False)
            
            print(f"Property Type: {property_data.get('property_type', 'N/A')}")
            print(f"Units: {property_data.get('units', 'N/A')}")
            print(f"Square Footage: {property_data.get('square_footage', 'N/A')}")
            print(f"Year Built: {property_data.get('year_built', 'N/A')}")
            print(f"Estimated Value: ${property_data.get('estimated_value', 'N/A'):,}" if property_data.get('estimated_value') else "Estimated Value: N/A")
            print()
            print(f"📈 Data Quality:")
            print(f"  Sources: {sources}")
            print(f"  Confidence: {confidence}%")
            print(f"  Is Estimated: {is_estimated}")
            print(f"  Notes: {data_quality.get('notes', 'N/A')}")
            
            # Determine data source
            if "ATTOM" in str(sources):
                print("✅ SUCCESS: Real ATTOM Data Retrieved!")
            elif "Gemini" in str(sources):
                print("✅ SUCCESS: Gemini AI Estimation Used!")
                
                # Show Gemini-specific data
                market_data = property_data.get('market_data', {})
                neighborhood_info = property_data.get('neighborhood_info', {})
                
                if market_data:
                    print(f"💰 Market Data:")
                    print(f"  Avg Rent/Unit: ${market_data.get('avg_rent_per_unit', 'N/A')}")
                    print(f"  Est Cap Rate: {market_data.get('estimated_cap_rate', 'N/A')}%")
                
                if neighborhood_info:
                    print(f"🏘️ Neighborhood: {neighborhood_info.get('area_description', 'N/A')[:100]}...")
            else:
                print("⚠️ Fallback: Minimal data returned")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            
        print()

if __name__ == "__main__":
    asyncio.run(test_attom_and_gemini())
