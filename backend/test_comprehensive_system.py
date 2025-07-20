#!/usr/bin/env python3
"""
Test the comprehensive property data system with ATTOM API and Gemini AI fallback
"""
import asyncio
import os
import sys
sys.path.append('/Volumes/project/intern/proppulse-ai/backend')

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from services.external_apis import ExternalAPIService
import json

async def test_comprehensive_system():
    """Test the complete property data system"""
    print("🧪 Testing Comprehensive Property Data System")
    print("=" * 60)
    
    # Test addresses
    test_addresses = [
        "1234 Santa Monica Blvd, West Hollywood, CA 90069",
        "456 Rodeo Drive, Beverly Hills, CA 90210",
        "789 Ocean Ave, Santa Monica, CA 90401"
    ]
    
    # Initialize service
    service = ExternalAPIService()
    
    # Check configuration
    print("🔧 System Configuration:")
    print(f"  ATTOM API Key: {'✅ Configured' if os.getenv('ATTOM_API_KEY') else '❌ Missing'}")
    print(f"  Gemini AI: {'✅ Configured' if service.gemini_model else '❌ Missing'}")
    print()
    
    for i, address in enumerate(test_addresses, 1):
        print(f"📍 Test {i}: {address}")
        print("-" * 50)
        
        try:
            # Get property data
            property_data = await service.get_property_data(address)
            
            # Display results
            print(f"Property Type: {property_data.get('property_type', 'N/A')}")
            print(f"Units: {property_data.get('units', 'N/A')}")
            print(f"Square Footage: {property_data.get('square_footage', 'N/A'):,}" if property_data.get('square_footage') else "Square Footage: N/A")
            print(f"Year Built: {property_data.get('year_built', 'N/A')}")
            print(f"Estimated Value: ${property_data.get('estimated_value', 0):,}" if property_data.get('estimated_value') else "Estimated Value: $0")
            
            # Market data
            market_data = property_data.get('market_data', {})
            if market_data:
                print(f"Monthly Rent/Unit: ${market_data.get('avg_rent_per_unit', 0):,}")
                print(f"Cap Rate: {market_data.get('estimated_cap_rate', 0)}%")
                print(f"Price/SqFt: ${market_data.get('price_per_sqft', 0)}")
            
            # Data quality
            data_quality = property_data.get('data_quality', {})
            sources = data_quality.get('sources', [])
            confidence = data_quality.get('confidence', 0)
            
            print(f"\n📊 Data Quality:")
            print(f"  Sources: {', '.join(sources)}")
            print(f"  Confidence: {confidence}%")
            print(f"  Is Estimated: {data_quality.get('is_estimated_data', False)}")
            print(f"  Notes: {data_quality.get('notes', 'N/A')}")
            
            # Check data source
            if "ATTOM" in str(sources):
                print("✅ SUCCESS: Real ATTOM Data!")
            elif "Gemini" in str(sources):
                print("🤖 SUCCESS: Gemini AI Estimation!")
            elif "Address Analysis" in str(sources):
                print("📋 SUCCESS: Intelligent Fallback Data!")
            
            print()
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            print()
    
    print("🏁 Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_comprehensive_system())
