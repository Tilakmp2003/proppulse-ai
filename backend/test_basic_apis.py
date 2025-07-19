#!/usr/bin/env python3
"""
Simple test for individual API components
"""
import asyncio
import httpx

async def test_basic_apis():
    print("Testing basic API connectivity...")
    
    # Test 1: OpenStreetMap Nominatim (geocoding)
    print("\n1. Testing OpenStreetMap Nominatim...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": "123 Main Street, Los Angeles, CA",
                    "format": "json",
                    "limit": 1,
                    "addressdetails": 1
                }
            )
            if response.status_code == 200:
                data = response.json()
                if data:
                    print(f"✅ OSM Success: Found {data[0].get('display_name', 'Unknown')}")
                else:
                    print("❌ OSM: No results found")
            else:
                print(f"❌ OSM: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ OSM Exception: {e}")
    
    # Test 2: US Census Geocoding
    print("\n2. Testing US Census API...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress",
                params={
                    "address": "123 Main Street, Los Angeles, CA",
                    "benchmark": "2020",
                    "format": "json"
                }
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("result", {}).get("addressMatches"):
                    print("✅ Census Success: Address found")
                else:
                    print("❌ Census: No address matches")
            else:
                print(f"❌ Census: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Census Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_basic_apis())
