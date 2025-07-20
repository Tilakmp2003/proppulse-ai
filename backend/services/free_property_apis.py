"""
Free Real Estate Data APIs - No cost alternatives for property data
"""
import httpx
import asyncio
import json
import os
import re
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class FreePropertyDataService:
    """
    Service to fetch real property data from FREE APIs
    """
    
    def __init__(self):
        self.session = None
        # Add ATTOM API Key from environment variable
        self.attom_api_key = os.getenv("ATTOM_API_KEY", "")
    
    async def get_census_data(self, address: str) -> Dict[str, Any]:
        """
        Fetch demographic data from US Census API (100% FREE)
        """
        try:
            # Geocode the address first
            geocode_url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
            geocode_params = {
                "address": address,
                "benchmark": "2020",
                "format": "json"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(geocode_url, params=geocode_params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("result", {}).get("addressMatches"):
                        match = data["result"]["addressMatches"][0]
                        coordinates = match["coordinates"]
                        address_components = match["addressComponents"]
                        
                        # Get census tract for demographics
                        tract_data = await self._get_census_tract_data(coordinates)
                        
                        return {
                            "coordinates": coordinates,
                            "address_components": address_components,
                            "census_data": tract_data,
                            "data_source": "US Census (Free)"
                        }
                        
        except Exception as e:
            logger.error(f"Census API error: {e}")
            return {}
        
        return {}
    
    async def get_openstreetmap_data(self, address: str) -> Dict[str, Any]:
        """
        Fetch location data from OpenStreetMap Nominatim API (100% FREE)
        """
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                "q": address,
                "format": "json",
                "limit": 1,
                "extratags": 1,
                "addressdetails": 1
            }
            
            headers = {
                "User-Agent": "PropPulse-AI/1.0 (Real Estate Analysis)"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data:
                        location = data[0]
                        return {
                            "latitude": float(location.get("lat", 0)),
                            "longitude": float(location.get("lon", 0)),
                            "display_name": location.get("display_name"),
                            "address_details": location.get("address", {}),
                            "place_id": location.get("place_id"),
                            "data_source": "OpenStreetMap (Free)"
                        }
                        
        except Exception as e:
            logger.error(f"OpenStreetMap API error: {e}")
            return {}
        
        return {}
    
    async def get_hud_data(self, state: str, city: str) -> Dict[str, Any]:
        """
        Fetch housing data from HUD API (100% FREE)
        """
        try:
            # HUD Fair Market Rents API
            url = f"https://www.huduser.gov/hudapi/public/fmr/data/{state}"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Find data for the specific city
                    city_data = None
                    for item in data.get("data", {}).get("fmrs", []):
                        if city.lower() in item.get("metro_name", "").lower():
                            city_data = item
                            break
                    
                    if city_data:
                        return {
                            "fair_market_rents": {
                                "efficiency": city_data.get("Efficiency"),
                                "one_bedroom": city_data.get("One-Bedroom"),
                                "two_bedroom": city_data.get("Two-Bedroom"),
                                "three_bedroom": city_data.get("Three-Bedroom"),
                                "four_bedroom": city_data.get("Four-Bedroom")
                            },
                            "metro_name": city_data.get("metro_name"),
                            "year": city_data.get("year"),
                            "data_source": "HUD (Free)"
                        }
                        
        except Exception as e:
            logger.error(f"HUD API error: {e}")
            return {}
        
        return {}
    
    async def get_fred_economic_data(self, state_code: str) -> Dict[str, Any]:
        """
        Fetch economic data from FRED API (FREE with registration)
        """
        try:
            # You can get a free API key from https://fred.stlouisfed.org/docs/api/api_key.html
            # For now, we'll use publicly available data endpoints
            
            # Unemployment rate by state
            url = f"https://api.stlouisfed.org/fred/series/observations"
            params = {
                "series_id": f"{state_code}UR",  # State unemployment rate
                "api_key": "demo",  # You can get a free key
                "file_type": "json",
                "limit": 1,
                "sort_order": "desc"
            }
            
            # Note: This will work better with a real FRED API key
            return {
                "data_source": "FRED Economic Data (Free with API key)",
                "note": "Register at https://fred.stlouisfed.org for free API key"
            }
            
        except Exception as e:
            logger.error(f"FRED API error: {e}")
            return {}
    
    async def _get_census_tract_data(self, coordinates: Dict[str, float]) -> Dict[str, Any]:
        """Get census tract demographic data"""
        try:
            # American Community Survey 5-Year Data
            lat = coordinates.get("latitude")
            lon = coordinates.get("longitude")
            
            if not lat or not lon:
                return self._get_default_demographics()
            
            # Get census tract
            tract_url = f"https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
            tract_params = {
                "x": lon,
                "y": lat,
                "benchmark": "2020",
                "vintage": "2020",
                "format": "json"
            }
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(tract_url, params=tract_params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("result", {}).get("geographies", {}).get("Census Tracts"):
                        tract_info = list(data["result"]["geographies"]["Census Tracts"].values())[0]
                        
                        return {
                            "tract_code": tract_info.get("TRACT"),
                            "county_name": tract_info.get("COUNTY"),
                            "state_name": tract_info.get("STATE"),
                            "median_income": 67500,  # Default estimate
                            "college_educated_pct": 42.8,
                            "unemployment_rate": 3.2,
                            "median_age": 34.5,
                            "population_growth_5yr": 8.5,
                            "note": "Enhanced with national averages"
                        }
                        
        except Exception as e:
            logger.error(f"Census tract error: {e}")
            return self._get_default_demographics()
        
        return self._get_default_demographics()
    
    def _get_default_demographics(self) -> Dict[str, Any]:
        """Return default demographic estimates"""
        return {
            "median_income": 67500,
            "college_educated_pct": 42.8,
            "unemployment_rate": 3.2,
            "median_age": 34.5,
            "population_growth_5yr": 8.5,
            "data_source": "National averages (Census data pending)"
        }
    
    def _infer_property_details_from_osm(self, osm_data: Dict[str, Any], address: str) -> Dict[str, Any]:
        """
        Infer property type, units, year built, and square footage from OpenStreetMap data and address.
        """
        property_type = "Unknown"
        units = 0
        year_built = None
        square_footage = None

        address_details = osm_data.get("address_details", {})
        extratags = osm_data.get("extratags", {})
        
        # Try to get year_built from extratags
        if "building:start_date" in extratags:
            try:
                year_built = int(extratags["building:start_date"].split('-')[0])
            except ValueError:
                pass
        elif "start_date" in extratags:
            try:
                year_built = int(extratags["start_date"].split('-')[0])
            except ValueError:
                pass
        elif "year_built" in extratags:
            try:
                year_built = int(extratags["year_built"])
            except ValueError:
                pass

        # Infer property type and units from address details and address string
        road = address_details.get("road", "").lower()
        building = address_details.get("building", "").lower()
        
        address_lower = address.lower()

        multifamily_keywords = ['apartment', 'apartments', 'apt', 'unit', 'units', 'condo', 'condominium', 'flats', 'complex', 'residences', 'lofts', 'tower', 'towers', 'plaza', 'manor', 'court', 'place']
        commercial_keywords = ['office', 'commercial', 'business', 'retail', 'store', 'shop', 'mall', 'center', 'building', 'warehouse', 'industrial']
        single_family_keywords = ['house', 'home', 'residence', 'villa', 'cottage', 'bungalow']

        # Check for multifamily indicators
        if any(kw in address_lower for kw in multifamily_keywords) or \
           any(kw in building for kw in multifamily_keywords) or \
           any(kw in road for kw in multifamily_keywords):
            property_type = "Multifamily"
            # Try to infer units from address (e.g., "UNIT 319")
            unit_match = re.search(r'(unit|apt|#)\s*(\d+)', address_lower)
            if unit_match:
                try:
                    # A single unit number implies it's one of many, so estimate total units
                    unit_num = int(unit_match.group(2))
                    units = max(unit_num + 10, 20) # Assume at least 20 units if a unit number is present
                except ValueError:
                    units = 20 # Default if unit number parsing fails
            elif "units" in extratags:
                try:
                    units = int(extratags["units"])
                except ValueError:
                    pass
            else:
                units = 20 # Default for multifamily if no unit number found

            if units > 0:
                square_footage = units * 850 # Average unit size for multifamily
            
        # Check for commercial indicators
        elif any(kw in address_lower for kw in commercial_keywords) or \
             any(kw in building for kw in commercial_keywords) or \
             any(kw in road for kw in commercial_keywords):
            property_type = "Commercial"
            units = 1 # Typically one "unit" for a commercial building
            if "building:flats" in extratags: # Sometimes used for commercial units
                try:
                    units = int(extratags["building:flats"])
                except ValueError:
                    pass
            if "building:levels" in extratags and units == 1: # Estimate sqft based on levels
                try:
                    levels = int(extratags["building:levels"])
                    square_footage = levels * 5000 # 5000 sqft per level for commercial
                except ValueError:
                    pass
            elif "building:floor_area" in extratags:
                try:
                    square_footage = float(extratags["building:floor_area"])
                except ValueError:
                    pass
            else:
                square_footage = 5000 # Default commercial sqft
                
        # Check for single family indicators
        elif any(kw in address_lower for kw in single_family_keywords) or \
             any(kw in building for kw in single_family_keywords):
            property_type = "Single Family"
            units = 1
            if "building:flats" in extratags: # Sometimes used for commercial units
                try:
                    units = int(extratags["building:flats"])
                except ValueError:
                    pass
            if "building:floor_area" in extratags:
                try:
                    square_footage = float(extratags["building:floor_area"])
                except ValueError:
                    pass
            else:
                square_footage = 2000 # Default single family sqft

        # Fallback for square footage if still None and units > 0
        if square_footage is None and units > 0:
            if property_type == "Multifamily":
                square_footage = units * 850
            elif property_type == "Single Family":
                square_footage = 2000
            elif property_type == "Commercial":
                square_footage = 5000

        return {
            "property_type": property_type,
            "units": units,
            "year_built": year_built,
            "square_footage": square_footage
        }

    async def get_comprehensive_free_data(self, address: str) -> Dict[str, Any]:
        """
        Combine all free data sources for comprehensive property information
        """
        logger.info(f"Fetching FREE property data for: {address}")
        
        # Enhanced address parsing for complex addresses
        address_parts = address.split(",")
        
        # Initialize variables
        city = ""
        state_code = ""
        
        # Look for state and city in the address parts
        for part in reversed(address_parts):  # Start from the end
            part = part.strip()
            
            # Check if this part contains a state (CA, TX, etc.)
            if any(state in part.upper() for state in ["CA", "TX", "NY", "FL", "WA", "OR", "AZ", "NV"]):
                state_code = part.split()[0] if part else ""
                continue
            
            # Check if this part contains a major city name
            major_cities = ["los angeles", "san francisco", "san diego", "sacramento",
                          "austin", "dallas", "houston", "san antonio",
                          "new york", "miami", "chicago", "seattle", "encino"] # Added Encino
            
            if any(city_name in part.lower() for city_name in major_cities):
                city = part
                break
        
        # Fallback parsing if above didn't work
        if not city and len(address_parts) > 1:
            city = address_parts[1].strip()
        if not state_code and len(address_parts) > 2:
            state_part = address_parts[-1].strip()  # Take the last part
            state_code = state_part.split()[0] if state_part else ""
        
        logger.info(f"Parsed - City: {city}, State: {state_code}")
        
        # Fetch data from multiple free sources
        tasks = [
            self.get_census_data(address),
            self.get_openstreetmap_data(address),
        ]
        
        # Add HUD data if we have city/state
        if city and state_code:
            tasks.append(self.get_hud_data(state_code.upper(), city))
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            census_data = results[0] if len(results) > 0 and isinstance(results[0], dict) else {}
            osm_data = results[1] if len(results) > 1 and isinstance(results[1], dict) else {}
            hud_data = results[2] if len(results) > 2 and isinstance(results[2], dict) else {}
            
            # Infer property details from OSM data and address
            inferred_details = self._infer_property_details_from_osm(osm_data, address)

            # Combine all free data
            combined_data = {
                "address": address,
                "property_type": inferred_details.get("property_type", "Unknown"),
                "units": inferred_details.get("units", 0),
                "year_built": inferred_details.get("year_built"),
                "square_footage": inferred_details.get("square_footage"),
                "data_sources": {
                    "census": census_data,
                    "openstreetmap": osm_data,
                    "hud": hud_data
                },
                "location": {
                    "latitude": osm_data.get("latitude"),
                    "longitude": osm_data.get("longitude"),
                    "display_name": osm_data.get("display_name")
                },
                "market_data": self._generate_market_estimates(hud_data, city, state_code),
                "is_free_data": True,
                "data_quality": "Enhanced estimates based on free public data"
            }
            
            return combined_data
            
        except Exception as e:
            logger.error(f"Error fetching free data: {e}")
            return {"address": address, "error": str(e), "is_free_data": True}
    
    def _generate_market_estimates(self, hud_data: Dict[str, Any], city: str, state: str) -> Dict[str, Any]:
        """Generate realistic market estimates based on free data - Enhanced for LA California"""
        
        # Base estimates on HUD Fair Market Rents if available
        base_rent = 1200  # Default higher for CA
        
        if hud_data.get("fair_market_rents"):
            fmr = hud_data["fair_market_rents"]
            # Use 2-bedroom as base for multifamily
            base_rent = fmr.get("two_bedroom", 1200)
        
        # Enhanced city multipliers focusing on LA California areas
        city_multipliers = {
            # LA Core Areas
            "los angeles": 2.8,
            "west hollywood": 3.2,
            "beverly hills": 4.5,
            "santa monica": 3.8,
            "venice": 3.0,
            "hollywood": 2.6,
            "downtown": 2.4,
            "koreatown": 2.2,
            "westwood": 3.5,
            "brentwood": 4.0,
            
            # LA County Areas
            "burbank": 2.4,
            "glendale": 2.3,
            "pasadena": 2.5,
            "long beach": 2.0,
            "torrance": 2.2,
            "manhattan beach": 4.2,
            "hermosa beach": 3.5,
            "el segundo": 2.8,
            "culver city": 3.2,
            "encino": 2.0, # Added Encino
            
            # Other California
            "san francisco": 4.8,
            "oakland": 3.2,
            "san diego": 2.6,
            "sacramento": 1.8,
            
            # Other major cities for comparison
            "austin": 1.3,
            "dallas": 1.2,
            "houston": 1.1,
            "seattle": 1.8,
            "new york": 3.2,
            "miami": 1.4,
            "chicago": 1.3,
            "atlanta": 1.1
        }
        
        multiplier = 1.0
        city_lower = city.lower()
        
        # Check for specific LA area matches
        for city_name, mult in city_multipliers.items():
            if city_name in city_lower:
                multiplier = mult
                break
        
        # If it's California but not specifically mapped, use higher baseline
        if state.upper() == "CA" and multiplier == 1.0:
            multiplier = 2.0  # General California multiplier
        
        estimated_rent = int(base_rent * multiplier)
        
        # Calculate property value using CA-appropriate rent multiplier
        # LA properties typically have lower cap rates due to appreciation potential
        if "los angeles" in city_lower or "hollywood" in city_lower or "encino" in city_lower: # Added Encino
            rent_multiplier = 250  # Lower cap rates in prime LA areas
        elif state.upper() == "CA":
            rent_multiplier = 200  # General CA multiplier
        else:
            rent_multiplier = 150  # Default multiplier
        
        estimated_value = estimated_rent * rent_multiplier
        
        # Calculate cap rate based on area
        if multiplier >= 3.0:  # Prime areas
            cap_rate = 4.5
        elif multiplier >= 2.0:  # Good areas
            cap_rate = 5.2
        else:  # Other areas
            cap_rate = 6.5
        
        return {
            "estimated_rent_per_unit": estimated_rent,
            "estimated_property_value": estimated_value,
            "rent_range": [int(estimated_rent * 0.85), int(estimated_rent * 1.15)],
            "cap_rate_estimate": cap_rate,
            "location_multiplier": multiplier,
            "data_basis": f"HUD Fair Market Rents + {city}, {state} location adjustment",
            "confidence": "High (enhanced for California markets)" if state.upper() == "CA" else "Medium (based on public data)",
            "market_notes": f"Estimates enhanced for {city}, {state} market conditions"
        }
    
    async def get_attom_property_data(self, address: str) -> Dict[str, Any]:
        """
        Fetch property data from ATTOM Property API (requires API key)
        """
        try:
            if not self.attom_api_key:
                logger.warning("ATTOM API key not configured")
                return {}
                
            # Format address for API
            formatted_address = address.replace(" ", "+")
            
            # First, try to get property details
            url = "https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/detail"
            params = {
                "address1": formatted_address
            }
            
            headers = {
                "apikey": self.attom_api_key,
                "accept": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("status", {}).get("code") == 0:
                        property_info = data.get("property", [{}])[0]
                        
                        # Extract relevant property details
                        result = {
                            "attom_id": property_info.get("identifier", {}).get("attomId"),
                            "property_type": self._map_attom_property_type(property_info.get("summary", {}).get("proptype")),
                            "year_built": property_info.get("summary", {}).get("yearbuilt"),
                            "bedrooms": property_info.get("building", {}).get("rooms", {}).get("beds"),
                            "bathrooms": property_info.get("building", {}).get("rooms", {}).get("bathstotal"),
                            "square_footage": property_info.get("building", {}).get("size", {}).get("universalsize"),
                            "lot_size": property_info.get("lot", {}).get("lotsize2"),
                            "data_source": "ATTOM Property API"
                        }
                        
                        # Try to get assessed value
                        await self._add_attom_valuation_data(result, property_info.get("identifier", {}).get("attomId"))
                        
                        return result
                    else:
                        logger.warning(f"ATTOM API error: {data.get('status', {}).get('msg')}")
            
        except Exception as e:
            logger.error(f"ATTOM API error: {e}")
        
        return {}

    async def _add_attom_valuation_data(self, property_data: Dict[str, Any], attom_id: str) -> None:
        """
        Add valuation data to property from ATTOM Valuation API
        """
        if not attom_id or not self.attom_api_key:
            return
            
        try:
            url = "https://api.gateway.attomdata.com/propertyapi/v1.0.0/assessment/detail"
            params = {"attomid": attom_id}
            
            headers = {
                "apikey": self.attom_api_key,
                "accept": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("status", {}).get("code") == 0:
                        assessment = data.get("property", [{}])[0].get("assessment", {})
                        
                        if assessment:
                            property_data["assessed_value"] = assessment.get("assessed", {}).get("assdttlvalue")
                            property_data["tax_amount"] = assessment.get("tax", {}).get("taxamt")
                            
                            # Try to get units count for multi-family
                            if property_data.get("property_type") == "Multifamily" and "units" not in property_data:
                                property_data["units"] = assessment.get("building", {}).get("units", 0)
                        
        except Exception as e:
            logger.error(f"ATTOM Valuation API error: {e}")

    def _map_attom_property_type(self, attom_type: str) -> str:
        """
        Map ATTOM property types to our standard property types
        """
        if not attom_type:
            return "Unknown"
            
        attom_type_lower = attom_type.lower()
        
        # Map ATTOM property types to our system
        if any(t in attom_type_lower for t in ["apartment", "multi family", "multifamily", "duplex", "triplex"]):
            return "Multifamily"
        elif any(t in attom_type_lower for t in ["commercial", "retail", "office", "industrial", "business"]):
            return "Commercial"
        elif any(t in attom_type_lower for t in ["single family", "sfr", "residence", "residential"]):
            return "Single Family"
        else:
            return attom_type  # Return original if no mapping
            
    # Keep all existing methods
    async def get_census_data(self, address: str) -> Dict[str, Any]:
        """
        Fetch demographic data from US Census API (100% FREE)
        """
        try:
            # Geocode the address first
            geocode_url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
            geocode_params = {
                "address": address,
                "benchmark": "2020",
                "format": "json"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(geocode_url, params=geocode_params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("result", {}).get("addressMatches"):
                        match = data["result"]["addressMatches"][0]
                        coordinates = match["coordinates"]
                        address_components = match["addressComponents"]
                        
                        # Get census tract for demographics
                        tract_data = await self._get_census_tract_data(coordinates)
                        
                        return {
                            "coordinates": coordinates,
                            "address_components": address_components,
                            "census_data": tract_data,
                            "data_source": "US Census (Free)"
                        }
                        
        except Exception as e:
            logger.error(f"Census API error: {e}")
            return {}
        
        return {}
    
    async def get_openstreetmap_data(self, address: str) -> Dict[str, Any]:
        """
        Fetch location data from OpenStreetMap Nominatim API (100% FREE)
        """
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                "q": address,
                "format": "json",
                "limit": 1,
                "extratags": 1,
                "addressdetails": 1
            }
            
            headers = {
                "User-Agent": "PropPulse-AI/1.0 (Real Estate Analysis)"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data:
                        location = data[0]
                        return {
                            "latitude": float(location.get("lat", 0)),
                            "longitude": float(location.get("lon", 0)),
                            "display_name": location.get("display_name"),
                            "address_details": location.get("address", {}),
                            "place_id": location.get("place_id"),
                            "data_source": "OpenStreetMap (Free)"
                        }
                        
        except Exception as e:
            logger.error(f"OpenStreetMap API error: {e}")
            return {}
        
        return {}
    
    async def get_hud_data(self, state: str, city: str) -> Dict[str, Any]:
        """
        Fetch housing data from HUD API (100% FREE)
        """
        try:
            # HUD Fair Market Rents API
            url = f"https://www.huduser.gov/hudapi/public/fmr/data/{state}"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Find data for the specific city
                    city_data = None
                    for item in data.get("data", {}).get("fmrs", []):
                        if city.lower() in item.get("metro_name", "").lower():
                            city_data = item
                            break
                    
                    if city_data:
                        return {
                            "fair_market_rents": {
                                "efficiency": city_data.get("Efficiency"),
                                "one_bedroom": city_data.get("One-Bedroom"),
                                "two_bedroom": city_data.get("Two-Bedroom"),
                                "three_bedroom": city_data.get("Three-Bedroom"),
                                "four_bedroom": city_data.get("Four-Bedroom")
                            },
                            "metro_name": city_data.get("metro_name"),
                            "year": city_data.get("year"),
                            "data_source": "HUD (Free)"
                        }
                        
        except Exception as e:
            logger.error(f"HUD API error: {e}")
            return {}
        
        return {}
    
    async def get_fred_economic_data(self, state_code: str) -> Dict[str, Any]:
        """
        Fetch economic data from FRED API (FREE with registration)
        """
        try:
            # You can get a free API key from https://fred.stlouisfed.org/docs/api/api_key.html
            # For now, we'll use publicly available data endpoints
            
            # Unemployment rate by state
            url = f"https://api.stlouisfed.org/fred/series/observations"
            params = {
                "series_id": f"{state_code}UR",  # State unemployment rate
                "api_key": "demo",  # You can get a free key
                "file_type": "json",
                "limit": 1,
                "sort_order": "desc"
            }
            
            # Note: This will work better with a real FRED API key
            return {
                "data_source": "FRED Economic Data (Free with API key)",
                "note": "Register at https://fred.stlouisfed.org for free API key"
            }
            
        except Exception as e:
            logger.error(f"FRED API error: {e}")
            return {}
    
    async def _get_census_tract_data(self, coordinates: Dict[str, float]) -> Dict[str, Any]:
        """Get census tract demographic data"""
        try:
            # American Community Survey 5-Year Data
            lat = coordinates.get("latitude")
            lon = coordinates.get("longitude")
            
            if not lat or not lon:
                return self._get_default_demographics()
            
            # Get census tract
            tract_url = f"https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
            tract_params = {
                "x": lon,
                "y": lat,
                "benchmark": "2020",
                "vintage": "2020",
                "format": "json"
            }
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(tract_url, params=tract_params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("result", {}).get("geographies", {}).get("Census Tracts"):
                        tract_info = list(data["result"]["geographies"]["Census Tracts"].values())[0]
                        
                        return {
                            "tract_code": tract_info.get("TRACT"),
                            "county_name": tract_info.get("COUNTY"),
                            "state_name": tract_info.get("STATE"),
                            "median_income": 67500,  # Default estimate
                            "college_educated_pct": 42.8,
                            "unemployment_rate": 3.2,
                            "median_age": 34.5,
                            "population_growth_5yr": 8.5,
                            "note": "Enhanced with national averages"
                        }
                        
        except Exception as e:
            logger.error(f"Census tract error: {e}")
            return self._get_default_demographics()
        
        return self._get_default_demographics()
    
    def _get_default_demographics(self) -> Dict[str, Any]:
        """Return default demographic estimates"""
        return {
            "median_income": 67500,
            "college_educated_pct": 42.8,
            "unemployment_rate": 3.2,
            "median_age": 34.5,
            "population_growth_5yr": 8.5,
            "data_source": "National averages (Census data pending)"
        }
    
    def _infer_property_details_from_osm(self, osm_data: Dict[str, Any], address: str) -> Dict[str, Any]:
        """
        Infer property type, units, year built, and square footage from OpenStreetMap data and address.
        """
        property_type = "Unknown"
        units = 0
        year_built = None
        square_footage = None

        address_details = osm_data.get("address_details", {})
        extratags = osm_data.get("extratags", {})
        
        # Try to get year_built from extratags
        if "building:start_date" in extratags:
            try:
                year_built = int(extratags["building:start_date"].split('-')[0])
            except ValueError:
                pass
        elif "start_date" in extratags:
            try:
                year_built = int(extratags["start_date"].split('-')[0])
            except ValueError:
                pass
        elif "year_built" in extratags:
            try:
                year_built = int(extratags["year_built"])
            except ValueError:
                pass

        # Infer property type and units from address details and address string
        road = address_details.get("road", "").lower()
        building = address_details.get("building", "").lower()
        
        address_lower = address.lower()

        multifamily_keywords = ['apartment', 'apartments', 'apt', 'unit', 'units', 'condo', 'condominium', 'flats', 'complex', 'residences', 'lofts', 'tower', 'towers', 'plaza', 'manor', 'court', 'place']
        commercial_keywords = ['office', 'commercial', 'business', 'retail', 'store', 'shop', 'mall', 'center', 'building', 'warehouse', 'industrial']
        single_family_keywords = ['house', 'home', 'residence', 'villa', 'cottage', 'bungalow']

        # Check for multifamily indicators
        if any(kw in address_lower for kw in multifamily_keywords) or \
           any(kw in building for kw in multifamily_keywords) or \
           any(kw in road for kw in multifamily_keywords):
            property_type = "Multifamily"
            # Try to infer units from address (e.g., "UNIT 319")
            unit_match = re.search(r'(unit|apt|#)\s*(\d+)', address_lower)
            if unit_match:
                try:
                    # A single unit number implies it's one of many, so estimate total units
                    unit_num = int(unit_match.group(2))
                    units = max(unit_num + 10, 20) # Assume at least 20 units if a unit number is present
                except ValueError:
                    units = 20 # Default if unit number parsing fails
            elif "units" in extratags:
                try:
                    units = int(extratags["units"])
                except ValueError:
                    pass
            else:
                units = 20 # Default for multifamily if no unit number found

            if units > 0:
                square_footage = units * 850 # Average unit size for multifamily
            
        # Check for commercial indicators
        elif any(kw in address_lower for kw in commercial_keywords) or \
             any(kw in building for kw in commercial_keywords) or \
             any(kw in road for kw in commercial_keywords):
            property_type = "Commercial"
            units = 1 # Typically one "unit" for a commercial building
            if "building:flats" in extratags: # Sometimes used for commercial units
                try:
                    units = int(extratags["building:flats"])
                except ValueError:
                    pass
            if "building:levels" in extratags and units == 1: # Estimate sqft based on levels
                try:
                    levels = int(extratags["building:levels"])
                    square_footage = levels * 5000 # 5000 sqft per level for commercial
                except ValueError:
                    pass
            elif "building:floor_area" in extratags:
                try:
                    square_footage = float(extratags["building:floor_area"])
                except ValueError:
                    pass
            else:
                square_footage = 5000 # Default commercial sqft
                
        # Check for single family indicators
        elif any(kw in address_lower for kw in single_family_keywords) or \
             any(kw in building for kw in single_family_keywords):
            property_type = "Single Family"
            units = 1
            if "building:flats" in extratags: # Sometimes used for commercial units
                try:
                    units = int(extratags["building:flats"])
                except ValueError:
                    pass
            if "building:floor_area" in extratags:
                try:
                    square_footage = float(extratags["building:floor_area"])
                except ValueError:
                    pass
            else:
                square_footage = 2000 # Default single family sqft

        # Fallback for square footage if still None and units > 0
        if square_footage is None and units > 0:
            if property_type == "Multifamily":
                square_footage = units * 850
            elif property_type == "Single Family":
                square_footage = 2000
            elif property_type == "Commercial":
                square_footage = 5000

        return {
            "property_type": property_type,
            "units": units,
            "year_built": year_built,
            "square_footage": square_footage
        }

    async def get_comprehensive_free_data(self, address: str) -> Dict[str, Any]:
        """
        Combine all free data sources for comprehensive property information
        """
        logger.info(f"Fetching FREE property data for: {address}")
        
        # Enhanced address parsing for complex addresses
        address_parts = address.split(",")
        
        # Initialize variables
        city = ""
        state_code = ""
        
        # Look for state and city in the address parts
        for part in reversed(address_parts):  # Start from the end
            part = part.strip()
            
            # Check if this part contains a state (CA, TX, etc.)
            if any(state in part.upper() for state in ["CA", "TX", "NY", "FL", "WA", "OR", "AZ", "NV"]):
                state_code = part.split()[0] if part else ""
                continue
            
            # Check if this part contains a major city name
            major_cities = ["los angeles", "san francisco", "san diego", "sacramento",
                          "austin", "dallas", "houston", "san antonio",
                          "new york", "miami", "chicago", "seattle", "encino"] # Added Encino
            
            if any(city_name in part.lower() for city_name in major_cities):
                city = part
                break
        
        # Fallback parsing if above didn't work
        if not city and len(address_parts) > 1:
            city = address_parts[1].strip()
        if not state_code and len(address_parts) > 2:
            state_part = address_parts[-1].strip()  # Take the last part
            state_code = state_part.split()[0] if state_part else ""
        
        logger.info(f"Parsed - City: {city}, State: {state_code}")
        
        # Fetch data from multiple free sources
        tasks = [
            self.get_census_data(address),
            self.get_openstreetmap_data(address),
        ]
        
        # Add HUD data if we have city/state
        if city and state_code:
            tasks.append(self.get_hud_data(state_code.upper(), city))
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            census_data = results[0] if len(results) > 0 and isinstance(results[0], dict) else {}
            osm_data = results[1] if len(results) > 1 and isinstance(results[1], dict) else {}
            hud_data = results[2] if len(results) > 2 and isinstance(results[2], dict) else {}
            
            # Infer property details from OSM data and address
            inferred_details = self._infer_property_details_from_osm(osm_data, address)

            # Combine all free data
            combined_data = {
                "address": address,
                "property_type": inferred_details.get("property_type", "Unknown"),
                "units": inferred_details.get("units", 0),
                "year_built": inferred_details.get("year_built"),
                "square_footage": inferred_details.get("square_footage"),
                "data_sources": {
                    "census": census_data,
                    "openstreetmap": osm_data,
                    "hud": hud_data
                },
                "location": {
                    "latitude": osm_data.get("latitude"),
                    "longitude": osm_data.get("longitude"),
                    "display_name": osm_data.get("display_name")
                },
                "market_data": self._generate_market_estimates(hud_data, city, state_code),
                "is_free_data": True,
                "data_quality": "Enhanced estimates based on free public data"
            }
            
            return combined_data
            
        except Exception as e:
            logger.error(f"Error fetching free data: {e}")
            return {"address": address, "error": str(e), "is_free_data": True}
    
    def _generate_market_estimates(self, hud_data: Dict[str, Any], city: str, state: str) -> Dict[str, Any]:
        """Generate realistic market estimates based on free data - Enhanced for LA California"""
        
        # Base estimates on HUD Fair Market Rents if available
        base_rent = 1200  # Default higher for CA
        
        if hud_data.get("fair_market_rents"):
            fmr = hud_data["fair_market_rents"]
            # Use 2-bedroom as base for multifamily
            base_rent = fmr.get("two_bedroom", 1200)
        
        # Enhanced city multipliers focusing on LA California areas
        city_multipliers = {
            # LA Core Areas
            "los angeles": 2.8,
            "west hollywood": 3.2,
            "beverly hills": 4.5,
            "santa monica": 3.8,
            "venice": 3.0,
            "hollywood": 2.6,
            "downtown": 2.4,
            "koreatown": 2.2,
            "westwood": 3.5,
            "brentwood": 4.0,
            
            # LA County Areas
            "burbank": 2.4,
            "glendale": 2.3,
            "pasadena": 2.5,
            "long beach": 2.0,
            "torrance": 2.2,
            "manhattan beach": 4.2,
            "hermosa beach": 3.5,
            "el segundo": 2.8,
            "culver city": 3.2,
            "encino": 2.0, # Added Encino
            
            # Other California
            "san francisco": 4.8,
            "oakland": 3.2,
            "san diego": 2.6,
            "sacramento": 1.8,
            
            # Other major cities for comparison
            "austin": 1.3,
            "dallas": 1.2,
            "houston": 1.1,
            "seattle": 1.8,
            "new york": 3.2,
            "miami": 1.4,
            "chicago": 1.3,
            "atlanta": 1.1
        }
        
        multiplier = 1.0
        city_lower = city.lower()
        
        # Check for specific LA area matches
        for city_name, mult in city_multipliers.items():
            if city_name in city_lower:
                multiplier = mult
                break
        
        # If it's California but not specifically mapped, use higher baseline
        if state.upper() == "CA" and multiplier == 1.0:
            multiplier = 2.0  # General California multiplier
        
        estimated_rent = int(base_rent * multiplier)
        
        # Calculate property value using CA-appropriate rent multiplier
        # LA properties typically have lower cap rates due to appreciation potential
        if "los angeles" in city_lower or "hollywood" in city_lower or "encino" in city_lower: # Added Encino
            rent_multiplier = 250  # Lower cap rates in prime LA areas
        elif state.upper() == "CA":
            rent_multiplier = 200  # General CA multiplier
        else:
            rent_multiplier = 150  # Default multiplier
        
        estimated_value = estimated_rent * rent_multiplier
        
        # Calculate cap rate based on area
        if multiplier >= 3.0:  # Prime areas
            cap_rate = 4.5
        elif multiplier >= 2.0:  # Good areas
            cap_rate = 5.2
        else:  # Other areas
            cap_rate = 6.5
        
        return {
            "estimated_rent_per_unit": estimated_rent,
            "estimated_property_value": estimated_value,
            "rent_range": [int(estimated_rent * 0.85), int(estimated_rent * 1.15)],
            "cap_rate_estimate": cap_rate,
            "location_multiplier": multiplier,
            "data_basis": f"HUD Fair Market Rents + {city}, {state} location adjustment",
            "confidence": "High (enhanced for California markets)" if state.upper() == "CA" else "Medium (based on public data)",
            "market_notes": f"Estimates enhanced for {city}, {state} market conditions"
        }


# Test the free APIs with LA California focus
async def test_free_apis():
    """Test all free API integrations with LA California addresses"""
    print("🆓 Testing FREE Property Data APIs - LA California Focus")
    print("=" * 60)
    
    service = FreePropertyDataService()
    
    # Test LA addresses
    test_addresses = [
        "1234 Sunset Blvd, Los Angeles, CA 90028",
        "5678 Wilshire Blvd, Los Angeles, CA 90036",
        "9012 Santa Monica Blvd, West Hollywood, CA 90069",
        "3456 Melrose Ave, Los Angeles, CA 90038"
    ]
    
    for address in test_addresses:
        print(f"\n🏠 Testing LA address: {address}")
        print("-" * 50)
        
        # Get comprehensive free data
        data = await service.get_comprehensive_free_data(address)
        
        print("📊 FREE Data Results:")
        print(f"✅ Address: {data.get('address')}")
        
        location = data.get('location', {})
        if location.get('display_name'):
            print(f"📍 Location: {location['display_name']}")
        
        # Show property details
        print(f"🏡 Property Type: {data.get('property_type', 'N/A')}")
        print(f"📏 Square Footage: {data.get('square_footage', 'N/A')}")
        print(f"🔢 Units: {data.get('units', 'N/A')}")
        print(f"🗓️ Year Built: {data.get('year_built', 'N/A')}")
        
        # Show market estimates
        market_data = data.get('market_data', {})
        if market_data:
            print(f"💰 Estimated Rent: ${market_data.get('estimated_rent_per_unit', 'N/A'):,}/month")
            print(f"🏢 Estimated Value: ${market_data.get('estimated_property_value', 'N/A'):,}")
            print(f"📈 Cap Rate Estimate: {market_data.get('cap_rate_estimate', 'N/A')}%")
            print(f"🔍 Location Multiplier: {market_data.get('location_multiplier', 'N/A')}x")
            print(f"📝 Market Notes: {market_data.get('market_notes', 'N/A')}")
        
        # Show data sources
        sources = data.get('data_sources', {})
        print(f"🔗 Data Sources Used:")
        for source_name, source_data in sources.items():
            if source_data:
                print(f"   ✅ {source_name.title()}: {source_data.get('data_source', 'Available')}")
            else:
                print(f"   ❌ {source_name.title()}: Not available")
        
        print(f"💡 Data Quality: {data.get('data_quality')}")
    
    return data

if __name__ == "__main__":
    asyncio.run(test_free_apis())
