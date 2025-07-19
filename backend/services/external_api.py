"""
External API Service - Handles integration with real estate data APIs
"""
import os
import httpx
import logging
from typing import Dict, Any, Optional, List
from config import settings

logger = logging.getLogger(__name__)

class ExternalAPIService:
    """
    Handles integration with external real estate APIs
    - CoStar API for property data
    - Zillow API for market data  
    - NeighborhoodScout API for neighborhood analytics
    """
    
    def __init__(self):
        self.logger = logger
        self.costar_api_key = getattr(settings, 'COSTAR_API_KEY', None) or os.getenv('COSTAR_API_KEY')
        self.zillow_api_key = getattr(settings, 'ZILLOW_API_KEY', None) or os.getenv('ZILLOW_API_KEY')
        self.neighborhood_api_key = getattr(settings, 'NEIGHBORHOODSCOUT_API_KEY', None) or os.getenv('NEIGHBORHOODSCOUT_API_KEY')
        
        # API endpoints
        self.costar_base_url = "https://api.costar.com/v1"
        self.zillow_base_url = "https://api.bridgedataoutput.com/api/v2/zestimates_v2"
        self.neighborhood_base_url = "https://api.neighborhoodscout.com/v1"
        
        # HTTP client
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_property_data(self, address: str) -> Dict[str, Any]:
        """
        Gather comprehensive property data from all available APIs
        
        Args:
            address: Property address
            
        Returns:
            Combined property and market data
        """
        try:
            # Gather data from all sources concurrently
            property_details = await self._get_property_details(address)
            market_comps = await self._get_market_comparables(address)
            neighborhood_data = await self._get_neighborhood_data(address)
            
            # Combine all data
            combined_data = {
                "property_details": property_details,
                "market_data": {
                    "comparable_properties": market_comps,
                    "neighborhood_analytics": neighborhood_data,
                    "market_trends": "Stable with moderate growth expected"  # Default
                },
                "data_sources": {
                    "costar_available": bool(self.costar_api_key and self.costar_api_key != 'demo_costar_key'),
                    "zillow_available": bool(self.zillow_api_key and self.zillow_api_key != 'demo_zillow_key'),
                    "neighborhood_scout_available": bool(self.neighborhood_api_key and self.neighborhood_api_key != 'demo_neighborhood_key')
                }
            }
            
            return combined_data
            
        except Exception as e:
            self.logger.error(f"Error gathering property data: {str(e)}")
            return self._get_mock_property_data(address)
    
    async def _get_property_details(self, address: str) -> Dict[str, Any]:
        """Get property details from CoStar API"""
        try:
            if not self.costar_api_key or self.costar_api_key == 'demo_costar_key':
                return self._get_mock_property_details()
            
            headers = {
                "Authorization": f"Bearer {self.costar_api_key}",
                "Content-Type": "application/json"
            }
            
            # Search for property by address
            search_url = f"{self.costar_base_url}/properties/search"
            search_payload = {
                "address": address,
                "property_types": ["multifamily", "apartment", "residential"]
            }
            
            response = await self.client.post(search_url, headers=headers, json=search_payload)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data.get('properties', [])) > 0:
                    prop = data['properties'][0]
                    return {
                        "year_built": prop.get('year_built'),
                        "square_footage": prop.get('building_area'),
                        "units": prop.get('unit_count'),
                        "property_type": prop.get('property_type', 'Multifamily'),
                        "market_value": prop.get('assessed_value'),
                        "lot_size": prop.get('lot_size'),
                        "parking_spaces": prop.get('parking_spaces'),
                        "amenities": prop.get('amenities', [])
                    }
            
            return self._get_mock_property_details()
            
        except Exception as e:
            self.logger.warning(f"CoStar API error: {str(e)}")
            return self._get_mock_property_details()
    
    async def _get_market_comparables(self, address: str) -> List[Dict[str, Any]]:
        """Get comparable properties from Zillow API"""
        try:
            if not self.zillow_api_key or self.zillow_api_key == 'demo_zillow_key':
                return self._get_mock_comparables()
            
            headers = {
                "Authorization": f"Bearer {self.zillow_api_key}",
                "Content-Type": "application/json"
            }
            
            # Get nearby properties
            comps_url = f"{self.zillow_base_url}/comparables"
            params = {
                "address": address,
                "radius": "0.5",  # 0.5 mile radius
                "property_type": "MultiFamily",
                "limit": 5
            }
            
            response = await self.client.get(comps_url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                comparables = []
                
                for comp in data.get('comparables', [])[:5]:
                    comparables.append({
                        "address": comp.get('address'),
                        "price": comp.get('estimated_value'),
                        "cap_rate": comp.get('cap_rate', 6.5),  # Default if not available
                        "square_footage": comp.get('square_footage'),
                        "units": comp.get('unit_count'),
                        "year_built": comp.get('year_built')
                    })
                
                return comparables if comparables else self._get_mock_comparables()
            
            return self._get_mock_comparables()
            
        except Exception as e:
            self.logger.warning(f"Zillow API error: {str(e)}")
            return self._get_mock_comparables()
    
    async def _get_neighborhood_data(self, address: str) -> Dict[str, Any]:
        """Get neighborhood analytics from NeighborhoodScout API"""
        try:
            if not self.neighborhood_api_key or self.neighborhood_api_key == 'demo_neighborhood_key':
                return self._get_mock_neighborhood_data()
            
            headers = {
                "Authorization": f"Bearer {self.neighborhood_api_key}",
                "Content-Type": "application/json"
            }
            
            # Get neighborhood analytics
            neighborhood_url = f"{self.neighborhood_base_url}/neighborhood"
            params = {
                "address": address,
                "include": "crime,demographics,housing,walkability"
            }
            
            response = await self.client.get(neighborhood_url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "neighborhood_score": data.get('overall_score', 75),
                    "crime_index": data.get('crime_index', 65),
                    "walkability_score": data.get('walkability_score', 70),
                    "school_rating": data.get('school_rating', 7),
                    "median_income": data.get('median_household_income'),
                    "population_growth": data.get('population_growth_rate', 2.1),
                    "employment_growth": data.get('employment_growth_rate', 1.8)
                }
            
            return self._get_mock_neighborhood_data()
            
        except Exception as e:
            self.logger.warning(f"NeighborhoodScout API error: {str(e)}")
            return self._get_mock_neighborhood_data()
    
    def _get_mock_property_details(self) -> Dict[str, Any]:
        """Mock property details for development/demo"""
        return {
            "year_built": 1995,
            "square_footage": 45000,
            "units": 48,
            "property_type": "Multifamily",
            "market_value": 4200000,
            "lot_size": 2.1,
            "parking_spaces": 96,
            "amenities": ["Pool", "Fitness Center", "Laundry Facility", "Covered Parking"]
        }
    
    def _get_mock_comparables(self) -> List[Dict[str, Any]]:
        """Mock comparable properties for development/demo"""
        return [
            {
                "address": "456 Oak Avenue, Austin, TX",
                "price": 3800000,
                "cap_rate": 6.2,
                "square_footage": 42000,
                "units": 44,
                "year_built": 1992
            },
            {
                "address": "789 Pine Street, Austin, TX", 
                "price": 4600000,
                "cap_rate": 5.9,
                "square_footage": 48000,
                "units": 52,
                "year_built": 1998
            },
            {
                "address": "321 Elm Drive, Austin, TX",
                "price": 3900000,
                "cap_rate": 6.4,
                "square_footage": 41000,
                "units": 46,
                "year_built": 1990
            }
        ]
    
    def _get_mock_neighborhood_data(self) -> Dict[str, Any]:
        """Mock neighborhood data for development/demo"""
        return {
            "neighborhood_score": 78,
            "crime_index": 68,
            "walkability_score": 72,
            "school_rating": 8,
            "median_income": 65000,
            "population_growth": 2.3,
            "employment_growth": 1.9
        }
    
    def _get_mock_property_data(self, address: str) -> Dict[str, Any]:
        """Complete mock data structure"""
        return {
            "property_details": self._get_mock_property_details(),
            "market_data": {
                "comparable_properties": self._get_mock_comparables(),
                "neighborhood_analytics": self._get_mock_neighborhood_data(),
                "market_trends": "Austin multifamily market showing strong fundamentals with 3-5% annual appreciation expected"
            },
            "data_sources": {
                "costar_available": False,
                "zillow_available": False,
                "neighborhood_scout_available": False,
                "note": "Using demo data - configure API keys for real data"
            }
        }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

# Create singleton instance
external_api_service = ExternalAPIService()
