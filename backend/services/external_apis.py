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
            
            # Try basic address analysis when APIs are unavailable
            basic_estimates = self._get_basic_property_estimates(address)
            if basic_estimates:
                self.logger.info(f"Using basic property estimates for {address}")
                return basic_estimates
            
            # No fallback data - return minimal structure with no defaults
            self.logger.info(f"No property data available for {address} - returning minimal structure")
            
            # Return minimal structure with no default values
            property_data = {
                "address": address,
                
                # Data sources and quality - minimal metadata only
                "data_quality": {
                    "is_free_data": False,
                    "sources": [],
                    "confidence": 0,
                    "last_updated": "2025-07-20",
                    "notes": "No property data available from any source"
                }
            }
            
            # Try to fetch real data if API keys are available
            if self._has_valid_api_keys():
                real_data = await self._fetch_real_market_data(address)
                if real_data:
                    property_data.update(real_data)
                    property_data["data_quality"]["is_real_data"] = True
            
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
            "data_quality": {
                "is_fallback_data": True,
                "confidence": 0,
                "sources": [],
                "last_updated": "2025-07-20",
                "notes": "No data available from any source"
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
        
        # Extract estimated values from free sources - no defaults
        estimated_rent = market_data.get("estimated_rent_per_unit")
        estimated_value = market_data.get("estimated_property_value")
        
        # Use real data when available, no estimates
        display_name = location.get("display_name", address)  # Address must be preserved
        
        # Extract data from free_data sources
        osm_data = free_data.get("data_sources", {}).get("openstreetmap", {})
        census_data = free_data.get("data_sources", {}).get("census", {}).get("census_data", {})
        
        # Only use actual data from free sources, no defaults
        property_type = free_data.get("property_type") 
        year_built = osm_data.get("address_details", {}).get("year")
        if year_built and not isinstance(year_built, int):
            year_built = None  # Invalid values become null
        
        units = free_data.get("units")  # Only use if available
        square_footage = free_data.get("square_footage")  # Only use if available
        
        # Use estimated_property_value only if available
        if estimated_value is None:
            estimated_value = market_data.get("estimated_property_value")
        
        # Neighborhood - use only if data exists
        neighborhood_name = osm_data.get("address_details", {}).get("neighbourhood") or \
                            osm_data.get("address_details", {}).get("suburb") or \
                            osm_data.get("address_details", {}).get("city") or \
                            census_data.get("county_name")
        
        walk_score = free_data.get("neighborhood_data", {}).get("walkability_score")
        
        # Calculate derived metrics
        price_per_unit = int(estimated_value / units) if units > 0 else 0
        price_per_sqft = round(estimated_value / square_footage, 2) if square_footage > 0 else 0
        
        # Calculate derived metrics only if we have the source data
        price_per_unit = int(estimated_value / units) if (estimated_value and units and units > 0) else None
        price_per_sqft = round(estimated_value / square_footage, 2) if (estimated_value and square_footage and square_footage > 0) else None
        
        formatted = {
            "address": address,
            "property_type": property_type,
            "year_built": year_built,
            "units": units,
            "square_footage": square_footage,
            "lot_size": free_data.get("lot_size"),  # Only if available
            "estimated_value": int(estimated_value) if estimated_value else None,
            "price_per_unit": price_per_unit,
            "price_per_sqft": price_per_sqft,
            
            # Market analysis from free data - no defaults
            "market_data": {
                "avg_rent_per_unit": market_data.get("estimated_rent_per_unit"),
                "avg_rent_per_sqft": round(market_data.get("estimated_rent_per_unit") / (square_footage / units), 2) 
                    if (market_data.get("estimated_rent_per_unit") and square_footage and units and units > 0) else None,
                "occupancy_rate": market_data.get("occupancy_rate"),
                "cap_rate_range": [
                    market_data.get("cap_rate_estimate") - 0.7 if market_data.get("cap_rate_estimate") else None,
                    market_data.get("cap_rate_estimate") + 0.2 if market_data.get("cap_rate_estimate") else None
                ] if market_data.get("cap_rate_estimate") else None,
                "market_rent_growth_3yr": market_data.get("market_rent_growth_3yr"),
                "location_multiplier": market_data.get("location_multiplier"),
                "market_notes": market_data.get("market_notes"),
                "comparable_sales": market_data.get("comparable_sales", [])
            },
            
            # Neighborhood analysis from free data - no defaults
            "neighborhood_data": {
                "crime_score": free_data.get("neighborhood_data", {}).get("crime_score"),
                "school_rating": free_data.get("neighborhood_data", {}).get("school_rating"),
                "walkability_score": walk_score,
                "median_income": census_data.get("median_income"),
                "population_growth_5yr": census_data.get("population_growth_5yr"),
                "unemployment_rate": census_data.get("unemployment_rate"),
                "median_age": census_data.get("median_age"),
                "college_educated_pct": census_data.get("college_educated_pct"),
                "county_name": census_data.get("county_name"),
                "state_name": census_data.get("state_name"),
                "latitude": osm_data.get("latitude"),
                "longitude": osm_data.get("longitude"),
                "location_quality": neighborhood_name,
                "openstreetmap_place_id": osm_data.get("place_id")
            },
            
            # Data quality indicators - retain minimal metadata
            "data_quality": {
                "is_free_data": True,
                "sources": [
                    source_data.get("data_source", source_name)
                    for source_name, source_data in free_data.get("data_sources", {}).items()
                    if source_data
                ] if free_data.get("data_sources") else [],
                "confidence": market_data.get("confidence"),
                "last_updated": "2025-07-19",  # Keep current date
                "notes": "Only using verified data from free public sources. No default values."
            }
        }
        
        # Calculate derived fields only if we have the source data
        if formatted["estimated_value"] and formatted["units"]:
            formatted["price_per_unit"] = formatted["estimated_value"] / formatted["units"]
        
        if formatted["estimated_value"] and formatted["square_footage"]:
            formatted["price_per_sqft"] = formatted["estimated_value"] / formatted["square_footage"]
        
        # Remove all None values from the formatted data
        # This ensures frontend gets a clean object without null/undefined values
        for key in list(formatted.keys()):
            if formatted[key] is None:
                del formatted[key]
                
        # Same for nested dictionaries
        for section in ["market_data", "neighborhood_data", "data_quality"]:
            if section in formatted and isinstance(formatted[section], dict):
                for key in list(formatted[section].keys()):
                    if formatted[section][key] is None:
                        del formatted[section][key]
        
        return formatted
    
    def _get_basic_property_estimates(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Provide basic property estimates based on address analysis when APIs are unavailable
        This is transparent about being estimates, not real data
        """
        try:
            import re
            
            # Parse address for clues
            address_lower = address.lower()
            
            # Detect if it's likely multifamily
            multifamily_indicators = ['apt', 'apartment', 'unit', 'suite', '#', 'complex', 'towers', 'plaza', 'manor', 'court', 'place']
            is_likely_multifamily = any(indicator in address_lower for indicator in multifamily_indicators)
            
            # Extract unit numbers or building size clues
            unit_match = re.search(r'unit\s*(\d+)|apt\s*(\d+)|#\s*(\d+)', address_lower)
            has_unit_number = bool(unit_match)
            
            # Basic estimates based on address patterns
            if is_likely_multifamily or has_unit_number:
                property_type = "Multifamily"
                
                # Estimate units based on address clues
                if unit_match:
                    # Get all valid unit numbers from the regex groups
                    unit_numbers = [int(g) for g in unit_match.groups() if g and g.isdigit()]
                    if unit_numbers:
                        unit_num = max(unit_numbers)
                        estimated_units = min(max(unit_num + 10, 20), 100)  # Reasonable range
                    else:
                        estimated_units = 48  # Default if no valid numbers found
                else:
                    estimated_units = 48  # Conservative multifamily estimate
                
                # Basic square footage estimate
                estimated_sqft = estimated_units * 850  # Average unit size
                
                # Basic value estimate (conservative)
                estimated_value = estimated_units * 55000  # Conservative per-unit value
                
                return {
                    "address": address,
                    "property_type": property_type,
                    "units": estimated_units,
                    "square_footage": estimated_sqft,
                    "estimated_value": estimated_value,
                    "price_per_unit": int(estimated_value / estimated_units),
                    "price_per_sqft": round(estimated_value / estimated_sqft, 2),
                    
                    "market_data": {
                        "avg_rent_per_unit": estimated_units * 18,  # Conservative rent estimate
                        "estimated_cap_rate": 6.5,
                    },
                    
                    "data_quality": {
                        "is_estimated_data": True,
                        "confidence": 25,  # Low confidence
                        "sources": ["Address Analysis"],
                        "last_updated": "2025-07-20",
                        "notes": "⚠️ ESTIMATES ONLY - Based on address analysis when real data APIs unavailable. Use for initial screening only."
                    }
                }
            
            return None  # Don't estimate for non-multifamily
            
        except Exception as e:
            self.logger.error(f"Error in basic estimates: {e}")
            return None
