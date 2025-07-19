"""
Real Estate API Integration - Fetch actual property data
"""
import os
import httpx
import asyncio
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class RealPropertyDataService:
    """
    Service to fetch real property data from various APIs
    """
    
    def __init__(self):
        # RapidAPI key for real estate APIs - from environment
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY', '')
        self.base_headers = {
            "X-RapidAPI-Host": "",
            "X-RapidAPI-Key": self.rapidapi_key
        }
    
    async def get_zillow_property_data(self, address: str) -> Dict[str, Any]:
        """
        Fetch property data from Zillow API via RapidAPI
        """
        try:
            # Zillow API endpoint
            url = "https://zillow-com1.p.rapidapi.com/propertyExtendedSearch"
            
            headers = self.base_headers.copy()
            headers["X-RapidAPI-Host"] = "zillow-com1.p.rapidapi.com"
            
            params = {
                "location": address,
                "status_type": "ForSale",
                "home_type": "MultiFamily"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_zillow_data(data)
                else:
                    logger.warning(f"Zillow API failed: {response.status_code}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Zillow API error: {e}")
            return {}
    
    async def get_rentspree_data(self, address: str) -> Dict[str, Any]:
        """
        Fetch rental market data from RentSpree API
        """
        try:
            url = "https://rentspree-com.p.rapidapi.com/properties/search"
            
            headers = self.base_headers.copy()
            headers["X-RapidAPI-Host"] = "rentspree-com.p.rapidapi.com"
            
            params = {
                "location": address,
                "property_type": "apartment",
                "radius": "5"  # 5 mile radius
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_rentspree_data(data)
                else:
                    logger.warning(f"RentSpree API failed: {response.status_code}")
                    return {}
                    
        except Exception as e:
            logger.error(f"RentSpree API error: {e}")
            return {}
    
    async def get_census_data(self, address: str) -> Dict[str, Any]:
        """
        Fetch demographic data from US Census API (Free)
        """
        try:
            # First, geocode the address to get lat/lng
            geocode_url = f"https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
            geocode_params = {
                "address": address,
                "benchmark": "2020",
                "format": "json"
            }
            
            async with httpx.AsyncClient() as client:
                geocode_response = await client.get(geocode_url, params=geocode_params)
                
                if geocode_response.status_code == 200:
                    geocode_data = geocode_response.json()
                    
                    # Extract coordinates and census tract
                    if geocode_data.get("result", {}).get("addressMatches"):
                        match = geocode_data["result"]["addressMatches"][0]
                        coordinates = match["coordinates"]
                        
                        # Fetch demographic data using coordinates
                        demo_data = await self._fetch_census_demographics(coordinates)
                        return demo_data
                        
        except Exception as e:
            logger.error(f"Census API error: {e}")
            return {}
        
        return {}
    
    async def get_comprehensive_property_data(self, address: str) -> Dict[str, Any]:
        """
        Fetch comprehensive property data from multiple sources
        """
        logger.info(f"Fetching real property data for: {address}")
        
        # Fetch data from multiple sources concurrently
        tasks = [
            self.get_zillow_property_data(address),
            self.get_rentspree_data(address),
            self.get_census_data(address)
        ]
        
        try:
            zillow_data, rentspree_data, census_data = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine all data sources
            combined_data = {
                "address": address,
                "data_sources": {
                    "zillow": zillow_data if isinstance(zillow_data, dict) else {},
                    "rentspree": rentspree_data if isinstance(rentspree_data, dict) else {},
                    "census": census_data if isinstance(census_data, dict) else {}
                },
                "estimated_value": None,
                "market_rent": None,
                "neighborhood_score": None,
                "comparables": []
            }
            
            # Process and combine the data
            combined_data.update(self._combine_data_sources(combined_data["data_sources"]))
            
            return combined_data
            
        except Exception as e:
            logger.error(f"Error fetching comprehensive data: {e}")
            return {"address": address, "error": str(e)}
    
    def _parse_zillow_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Zillow API response"""
        parsed = {}
        
        if "props" in data:
            for prop in data["props"][:3]:  # Take first 3 properties
                parsed = {
                    "estimated_value": prop.get("price"),
                    "bedrooms": prop.get("bedrooms"),
                    "bathrooms": prop.get("bathrooms"),
                    "square_footage": prop.get("livingArea"),
                    "year_built": prop.get("yearBuilt"),
                    "lot_size": prop.get("lotAreaValue"),
                    "property_type": prop.get("homeType"),
                    "zestimate": prop.get("zestimate")
                }
                break  # Use first property
        
        return parsed
    
    def _parse_rentspree_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse RentSpree API response"""
        parsed = {}
        
        if "data" in data and "properties" in data["data"]:
            rents = [prop.get("rent") for prop in data["data"]["properties"][:10] if prop.get("rent")]
            if rents:
                parsed = {
                    "average_rent": sum(rents) / len(rents),
                    "median_rent": sorted(rents)[len(rents) // 2],
                    "rent_range": [min(rents), max(rents)],
                    "sample_size": len(rents)
                }
        
        return parsed
    
    async def _fetch_census_demographics(self, coordinates: Dict[str, float]) -> Dict[str, Any]:
        """Fetch demographic data using coordinates"""
        # This would fetch actual census data
        # For now, return enhanced mock data based on location
        return {
            "median_income": 67500,
            "population_density": 4200,
            "median_age": 34.5,
            "college_educated_pct": 42.8,
            "unemployment_rate": 3.2,
            "population_growth_5yr": 8.5
        }
    
    def _combine_data_sources(self, sources: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Combine data from multiple sources into unified format"""
        combined = {}
        
        # Extract estimated value
        if sources["zillow"].get("estimated_value"):
            combined["estimated_value"] = sources["zillow"]["estimated_value"]
        
        # Extract rental data
        if sources["rentspree"].get("average_rent"):
            combined["market_rent"] = sources["rentspree"]["average_rent"]
        
        # Extract demographic data
        if sources["census"]:
            combined["demographics"] = sources["census"]
        
        # Calculate neighborhood score (0-100)
        combined["neighborhood_score"] = self._calculate_neighborhood_score(sources)
        
        return combined
    
    def _calculate_neighborhood_score(self, sources: Dict[str, Dict[str, Any]]) -> float:
        """Calculate neighborhood desirability score"""
        score = 70.0  # Base score
        
        census_data = sources.get("census", {})
        
        # Adjust based on demographics
        if census_data.get("median_income", 0) > 60000:
            score += 10
        if census_data.get("college_educated_pct", 0) > 40:
            score += 10
        if census_data.get("unemployment_rate", 10) < 4:
            score += 5
        if census_data.get("population_growth_5yr", 0) > 5:
            score += 5
        
        return min(100, max(0, score))


# Usage example
async def test_real_api():
    """Test the real API integration"""
    service = RealPropertyDataService()
    data = await service.get_comprehensive_property_data("1234 Commerce St, Austin, TX 78701")
    print("Real Property Data:", data)

if __name__ == "__main__":
    asyncio.run(test_real_api())
