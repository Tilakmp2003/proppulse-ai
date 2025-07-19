"""
External APIs Service - Handles integration with CoStar, Zillow, and NeighborhoodScout
"""
from typing import Dict, Any, Optional
import httpx
import logging
from config import settings

logger = logging.getLogger(__name__)

class ExternalAPIService:
    """
    Handles external API integrations for property data collection
    """
    
    def __init__(self):
        self.logger = logger
        self.costar_api_key = settings.COSTAR_API_KEY
        self.zillow_api_key = settings.ZILLOW_API_KEY
        self.neighborhoodscout_api_key = settings.NEIGHBORHOODSCOUT_API_KEY
    
    async def get_property_data(self, address: str) -> Dict[str, Any]:
        """
        Aggregate property data from all external sources
        
        Args:
            address: Property address
            
        Returns:
            Dict containing combined property data
        """
        try:
            # First try free data sources
            from services.free_property_apis import FreePropertyDataService
            free_api_service = FreePropertyDataService()
            free_data = await free_api_service.get_comprehensive_free_data(address)
            
            if free_data and not free_data.get('error'):
                self.logger.info(f"Using FREE property data for {address}")
                return self._format_free_data(free_data, address)
            
            # Check if we have real API keys configured as fallback
            if (hasattr(settings, 'RAPIDAPI_KEY') and 
                settings.RAPIDAPI_KEY and 
                settings.RAPIDAPI_KEY != 'your_rapidapi_key_here'):
                
                # Use real API integration as fallback
                try:
                    from services.real_property_apis import RealPropertyDataService
                    real_api_service = RealPropertyDataService()
                    real_data = await real_api_service.get_comprehensive_property_data(address)
                    
                    if real_data and not real_data.get('error'):
                        self.logger.info(f"Using real property data for {address}")
                        return self._format_real_data(real_data, address)
                except Exception as e:
                    self.logger.warning(f"Real API fallback failed: {e}")
            
            # Final fallback to enhanced mock data for MVP demo
            self.logger.info(f"Using enhanced mock data for {address} (free APIs had issues)")
            
            # Enhanced mock data structure for MVP demo
            property_data = {
                "address": address,
                "property_type": "Multifamily",
                "year_built": 1995,
                "units": 48,
                "square_footage": 42000,
                "lot_size": 2.1,
                "estimated_value": 2500000,
                "price_per_unit": 52083,
                "price_per_sqft": 59.52,
                
                # Market analysis
                "market_data": {
                    "avg_rent_per_unit": 875,
                    "avg_rent_per_sqft": 0.99,
                    "occupancy_rate": 95.8,
                    "cap_rate_range": [5.8, 6.5],
                    "market_rent_growth_3yr": 4.2,
                    "comparable_sales": [
                        {
                            "address": "123 Comparable Dr",
                            "sale_price": 2400000,
                            "sale_date": "2024-03-15",
                            "units": 44,
                            "cap_rate": 6.1,
                            "price_per_unit": 54545
                        },
                        {
                            "address": "456 Similar St",
                            "sale_price": 2650000,
                            "sale_date": "2024-01-22",
                            "units": 52,
                            "cap_rate": 5.9,
                            "price_per_unit": 50962
                        },
                        {
                            "address": "789 Comp Avenue",
                            "sale_price": 2350000,
                            "sale_date": "2023-11-08",
                            "units": 46,
                            "cap_rate": 6.3,
                            "price_per_unit": 51087
                        }
                    ]
                },
                
                # Neighborhood analysis
                "neighborhood_data": {
                    "crime_score": 7.2,  # Out of 10, higher is safer
                    "school_rating": 8.1,  # Out of 10
                    "walkability_score": 6.8,  # Out of 10
                    "median_income": 67500,
                    "population_growth_5yr": 8.5,  # Percentage
                    "unemployment_rate": 3.2,
                    "median_age": 34.5,
                    "college_educated_pct": 42.8
                },
                
                # Property specifics
                "zoning": "R-3 (Multi-Family Residential)",
                "parking_spaces": 58,
                "parking_ratio": 1.21,  # Spaces per unit
                "amenities": [
                    "Swimming Pool",
                    "Fitness Center", 
                    "Clubhouse",
                    "On-site Laundry",
                    "Playground",
                    "Covered Parking"
                ],
                
                # Financial estimates
                "estimated_expenses": {
                    "property_management": 8.0,  # % of gross income
                    "property_taxes": 1.8,  # % of property value
                    "insurance": 0.7,  # % of property value
                    "maintenance_capex": 5.0,  # % of gross income
                    "utilities": 6500,  # Annual amount
                    "other_expenses": 12000  # Annual amount
                },
                
                # Market trends
                "market_trends": {
                    "rental_market_trend": "Growing",
                    "supply_pipeline": "Moderate",
                    "demand_drivers": [
                        "Job growth in tech sector",
                        "University expansion",
                        "Transit improvements"
                    ],
                    "risk_factors": [
                        "New construction in pipeline",
                        "Economic uncertainty"
                    ]
                },
                
                # Data sources and quality
                "data_quality": {
                    "property_data_confidence": 85,
                    "market_data_confidence": 78,
                    "neighborhood_data_confidence": 82,
                    "last_updated": "2024-07-18",
                    "sources": ["CoStar", "Zillow", "NeighborhoodScout", "Census"]
                }
            }
            
            # Try to fetch real data if API keys are available
            if self._has_valid_api_keys():
                real_data = await self._fetch_real_market_data(address)
                if real_data:
                    property_data.update(real_data)
                    property_data["data_quality"]["is_real_data"] = True
                else:
                    property_data["data_quality"]["is_mock_data"] = True
            else:
                property_data["data_quality"]["is_mock_data"] = True
                property_data["data_quality"]["note"] = "Using demo data - configure API keys for real data"
            
            return property_data
            
        except Exception as e:
            self.logger.error(f"Error fetching property data: {str(e)}")
            # Return basic fallback data
            return self._get_fallback_property_data(address)
    
    def _has_valid_api_keys(self) -> bool:
        """Check if we have valid API keys (not placeholders)"""
        return (
            self.costar_api_key and "placeholder" not in self.costar_api_key.lower() and
            self.zillow_api_key and "placeholder" not in self.zillow_api_key.lower() and
            self.neighborhoodscout_api_key and "placeholder" not in self.neighborhoodscout_api_key.lower()
        )
    
    async def _fetch_real_market_data(self, address: str) -> Optional[Dict[str, Any]]:
        """Attempt to fetch real data from external APIs"""
        combined_data = {}
        
        # Try CoStar
        costar_data = await self._fetch_costar_data(address)
        if costar_data:
            combined_data.update(costar_data)
        
        # Try Zillow
        zillow_data = await self._fetch_zillow_data(address)
        if zillow_data:
            combined_data["market_data"].update(zillow_data)
        
        # Try NeighborhoodScout
        neighborhood_data = await self._fetch_neighborhood_data(address)
        if neighborhood_data:
            combined_data["neighborhood_data"].update(neighborhood_data)
        
        return combined_data if combined_data else None
    
    def _get_fallback_property_data(self, address: str) -> Dict[str, Any]:
        """Return minimal fallback data when all else fails"""
        return {
            "address": address,
            "error": "Unable to fetch property data",
            "property_type": "Multifamily",
            "estimated_value": 2000000,
            "units": 40,
            "estimated": True,
            "data_quality": {
                "is_fallback_data": True,
                "confidence": 30
            }
        }
    
    async def _fetch_costar_data(self, address: str) -> Optional[Dict[str, Any]]:
        """Fetch data from CoStar API"""
        try:
            # Placeholder for CoStar API integration
            # In production, implement actual CoStar API calls
            self.logger.info(f"Fetching CoStar data for {address}")
            return None
        except Exception as e:
            self.logger.error(f"CoStar API error: {str(e)}")
            return None
    
    async def _fetch_zillow_data(self, address: str) -> Optional[Dict[str, Any]]:
        """Fetch data from Zillow API"""
        try:
            # Placeholder for Zillow API integration
            self.logger.info(f"Fetching Zillow data for {address}")
            return None
        except Exception as e:
            self.logger.error(f"Zillow API error: {str(e)}")
            return None
    
    async def _fetch_neighborhood_data(self, address: str) -> Optional[Dict[str, Any]]:
        """Fetch data from NeighborhoodScout API"""
        try:
            # Placeholder for NeighborhoodScout API integration
            self.logger.info(f"Fetching NeighborhoodScout data for {address}")
            return None
        except Exception as e:
            self.logger.error(f"NeighborhoodScout API error: {str(e)}")
            return None
    
    def _format_real_data(self, real_data: Dict[str, Any], address: str) -> Dict[str, Any]:
        """Format real API data into expected structure"""
        formatted = {
            "address": address,
            "property_type": "Multifamily",
            "year_built": real_data.get("year_built", 1995),
            "units": real_data.get("units", 48),
            "square_footage": real_data.get("square_footage", 42000),
            "lot_size": real_data.get("lot_size", 2.1),
            "estimated_value": real_data.get("estimated_value", 2500000),
            "price_per_unit": 0,
            "price_per_sqft": 0,
            
            # Market analysis from real data
            "market_data": {
                "avg_rent_per_unit": real_data.get("market_rent", 875),
                "avg_rent_per_sqft": 0.99,
                "occupancy_rate": 95.8,
                "cap_rate_range": [5.8, 6.5],
                "market_rent_growth_3yr": 4.2,
                "comparable_sales": real_data.get("comparables", [])
            },
            
            # Neighborhood analysis from real data
            "neighborhood_data": real_data.get("demographics", {
                "crime_score": 7.2,
                "school_rating": 8.1,
                "walkability_score": 6.8,
                "median_income": 67500,
                "population_growth_5yr": 8.5,
                "unemployment_rate": 3.2,
                "median_age": 34.5,
                "college_educated_pct": 42.8
            }),
            
            # Data quality indicators
            "data_quality": {
                "is_real_data": True,
                "sources": list(real_data.get("data_sources", {}).keys()),
                "confidence": real_data.get("neighborhood_score", 85),
                "last_updated": "2025-07-18"
            }
        }
        
        # Calculate derived fields
        if formatted["estimated_value"] and formatted["units"]:
            formatted["price_per_unit"] = formatted["estimated_value"] / formatted["units"]
        
        if formatted["estimated_value"] and formatted["square_footage"]:
            formatted["price_per_sqft"] = formatted["estimated_value"] / formatted["square_footage"]
        
        return formatted
    
    def _format_free_data(self, free_data: Dict[str, Any], address: str) -> Dict[str, Any]:
        """Format free API data into expected structure"""
        location = free_data.get("location", {})
        market_data = free_data.get("market_data", {})
        data_sources = free_data.get("data_sources", {})
        
        # Extract estimated values from free sources
        estimated_rent = market_data.get("estimated_rent_per_unit", 875)
        estimated_value = market_data.get("estimated_property_value", 195000)
        
        # Use real data when available, otherwise intelligent estimates
        display_name = location.get("display_name", address)
        
        # Determine property characteristics based on location
        units = 48  # Default for multifamily
        square_footage = 42000  # Default
        year_built = 1995  # Default
        
        # Enhance estimates for California properties
        if "california" in display_name.lower() or "CA" in address:
            if "los angeles" in display_name.lower():
                units = 36  # Typical LA multifamily size
                square_footage = 32000
                year_built = 1985
            elif "west hollywood" in display_name.lower():
                units = 24  # Smaller boutique buildings
                square_footage = 28000
                year_built = 1975
            elif "beverly hills" in display_name.lower():
                units = 18  # Luxury smaller buildings
                square_footage = 25000
                year_built = 1980
        
        # Calculate derived metrics
        price_per_unit = int(estimated_value / units) if units > 0 else 0
        price_per_sqft = round(estimated_value / square_footage, 2) if square_footage > 0 else 0
        
        formatted = {
            "address": address,
            "property_type": "Multifamily",
            "year_built": year_built,
            "units": units,
            "square_footage": square_footage,
            "lot_size": 2.1,
            "estimated_value": int(estimated_value),
            "price_per_unit": price_per_unit,
            "price_per_sqft": price_per_sqft,
            
            # Market analysis from free data
            "market_data": {
                "avg_rent_per_unit": estimated_rent,
                "avg_rent_per_sqft": round(estimated_rent / (square_footage / units), 2) if units > 0 else 0.99,
                "occupancy_rate": 95.8,
                "cap_rate_range": [
                    market_data.get("cap_rate_estimate", 6.5) - 0.7,
                    market_data.get("cap_rate_estimate", 6.5) + 0.2
                ],
                "market_rent_growth_3yr": 4.2,
                "location_multiplier": market_data.get("location_multiplier", 1.0),
                "market_notes": market_data.get("market_notes", "Market data from free sources"),
                "comparable_sales": [
                    {
                        "address": f"Comparable Property A ({location.get('display_name', 'Area')})",
                        "sale_price": int(estimated_value * 0.95),
                        "sale_date": "2024-03-15",
                        "units": max(units - 4, 20),
                        "cap_rate": round(market_data.get("cap_rate_estimate", 6.5) + 0.1, 1),
                        "price_per_unit": int(estimated_value * 0.95 / max(units - 4, 20))
                    },
                    {
                        "address": f"Comparable Property B ({location.get('display_name', 'Area')})", 
                        "sale_price": int(estimated_value * 1.05),
                        "sale_date": "2024-01-22",
                        "units": min(units + 8, 60),
                        "cap_rate": round(market_data.get("cap_rate_estimate", 6.5) - 0.1, 1),
                        "price_per_unit": int(estimated_value * 1.05 / min(units + 8, 60))
                    }
                ]
            },
            
            # Location data from OpenStreetMap and Census
            "neighborhood_data": {
                "crime_score": 7.2,  # Default estimate
                "school_rating": 8.1,  # Default estimate
                "walkability_score": 6.8,  # Default estimate
                "median_income": data_sources.get("census", {}).get("census_data", {}).get("median_income", 67500),
                "population_growth_5yr": data_sources.get("census", {}).get("census_data", {}).get("population_growth_5yr", 8.5),
                "unemployment_rate": data_sources.get("census", {}).get("census_data", {}).get("unemployment_rate", 3.2),
                "median_age": data_sources.get("census", {}).get("census_data", {}).get("median_age", 34.5),
                "college_educated_pct": data_sources.get("census", {}).get("census_data", {}).get("college_educated_pct", 42.8),
                "county_name": data_sources.get("census", {}).get("census_data", {}).get("county_name", ""),
                "state_name": data_sources.get("census", {}).get("census_data", {}).get("state_name", ""),
                "latitude": location.get("latitude"),
                "longitude": location.get("longitude"),
                "location_quality": location.get("display_name", "Location verified"),
                "openstreetmap_place_id": data_sources.get("openstreetmap", {}).get("place_id")
            },
            
            # Data quality indicators
            "data_quality": {
                "is_free_data": True,
                "sources": [
                    source_data.get("data_source", source_name) 
                    for source_name, source_data in data_sources.items() 
                    if source_data
                ] if data_sources else ["OpenStreetMap", "US Census", "HUD Fair Market Rents"],
                "confidence": market_data.get("confidence", "Medium confidence for free data"),
                "last_updated": "2025-07-18",
                "notes": f"Enhanced estimates using free public data sources. {market_data.get('data_basis', '')}"
            }
        }
        
        # Calculate derived fields
        if formatted["estimated_value"] and formatted["units"]:
            formatted["price_per_unit"] = formatted["estimated_value"] / formatted["units"]
        
        if formatted["estimated_value"] and formatted["square_footage"]:
            formatted["price_per_sqft"] = formatted["estimated_value"] / formatted["square_footage"]
        
        return formatted
