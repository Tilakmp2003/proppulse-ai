"""
External API Service
Handles all interactions with external property data sources
"""
import os
import re
import json
import time
import random
import logging
import traceback
from typing import Dict, Any, List, Optional, Tuple

import httpx
import requests
from fastapi import HTTPException
import google.generativeai as genai

class ExternalAPIService:
    """
    Service for interacting with external property data APIs
    Combines free data sources to provide basic property information
    """
    
    def __init__(self):
        """Initialize the service with API credentials"""
        self.logger = logging.getLogger(__name__)
        self.api_keys = {
            "geocoding": os.getenv("GEOCODING_API_KEY", "demo"),
            "property_data": os.getenv("PROPERTY_DATA_API_KEY", "demo"),
            "walkscore": os.getenv("WALKSCORE_API_KEY", "demo")
        }
        
        # Initialize Gemini AI for property estimation
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key and gemini_key != 'your_gemini_api_key_here':
            genai.configure(api_key=gemini_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.gemini_model = None
        
        # Track API usage to avoid hitting limits
        self.api_call_counters = {}
        
    async def get_property_data(self, address: str) -> Dict[str, Any]:
        """
        Get property data prioritizing ATTOM API for real data, with intelligent fallback
        Returns comprehensive property data combining real sources and enhanced estimates
        """
        self.logger.info(f"Fetching property data for: {address}")
        
        # Validate address format first
        address_validation = self._validate_address_format(address)
        if address_validation:
            return {
                "error": address_validation,
                "address": address,
                "data_quality": {
                    "confidence": 0,
                    "sources": [],
                    "notes": f"Address validation failed: {address_validation}"
                }
            }
        
        try:
            # Use the enhanced free property data service with ATTOM integration
            from services.free_property_apis import FreePropertyDataService
            service = FreePropertyDataService()
            
            # First try ATTOM API for real data
            attom_data = await service.get_attom_property_data(address)
            
            if attom_data and attom_data.get("attom_id"):
                self.logger.info(f"Got REAL ATTOM property data for: {address}")
                
                # Format ATTOM data to our structure
                property_data = {
                    "address": attom_data.get("address", address),
                    "property_type": attom_data.get("property_type", "Unknown"),
                    "units": attom_data.get("units") or 1,
                    "building_area_sqft": attom_data.get("square_footage"),
                    "year_built": attom_data.get("year_built"),
                    "bedrooms": attom_data.get("bedrooms"),
                    "bathrooms": attom_data.get("bathrooms"),
                    "lot_size": attom_data.get("lot_size"),
                    "assessed_value": attom_data.get("assessed_value"),
                    "tax_amount": attom_data.get("tax_amount"),
                    "asking_price": f"${attom_data.get('assessed_value', 0):,}" if attom_data.get("assessed_value") else None
                }
                
                # Get location data to supplement
                free_data = await service.get_comprehensive_free_data(address)
                if free_data.get("location"):
                    property_data["location"] = free_data["location"]
                    
                # Add market estimates based on ATTOM data
                if free_data.get("market_data"):
                    property_data["market_estimates"] = free_data["market_data"]
                
                return {
                    "property_data": property_data,
                    "confidence_score": 95,
                    "data_sources": ["ATTOM Data API"],
                    "data_quality": {
                        "is_estimated_data": False,
                        "is_free_data": False,
                        "confidence": 95,
                        "sources": ["ATTOM Data API"],
                        "last_updated": "2025-10-03",
                        "notes": "Verified property records from ATTOM Data API"
                    }
                }
            
            # If no ATTOM data, use enhanced free APIs for comprehensive estimates
            self.logger.info(f"ATTOM data not available, using enhanced free data sources for: {address}")
            
            property_data = await service.get_comprehensive_free_data(address)
            
            # Check if we got meaningful data
            if (property_data and 
                property_data.get("location", {}).get("latitude") and
                property_data.get("property_type") != "Unknown"):
                
                self.logger.info(f"Got enhanced property data from free sources for: {address}")
                
                # Get AI-enhanced neighborhood and walkability data
                neighborhood_data = await self._get_gemini_property_estimation(address)
                
                # Format the data to match frontend expectations
                formatted_data = {
                    "address": property_data.get("address", address),
                    "property_type": property_data.get("property_type", "Residential"),
                    "units": property_data.get("units", 1),
                    "building_area_sqft": property_data.get("square_footage"),
                    "year_built": property_data.get("year_built"),
                    "neighborhood": neighborhood_data.get("neighborhood", property_data.get("location", {}).get("display_name", "").split(",")[1:3]),
                    "walk_score": neighborhood_data.get("walk_score", 50),
                    "walkability_notes": neighborhood_data.get("walkability_notes", ""),
                    "neighborhood_description": neighborhood_data.get("neighborhood_description", "")
                }
                
                # Add market estimates if available
                market_data = property_data.get("market_data", {})
                if market_data:
                    formatted_data["asking_price"] = f"${market_data.get('estimated_property_value', 0):,}"
                    formatted_data["estimated_rent"] = f"${market_data.get('estimated_rent_per_unit', 0):,}/month"
                    formatted_data["cap_rate"] = f"{market_data.get('cap_rate_estimate', 0)}%"
                
                # Determine confidence based on data quality
                confidence = 85 if property_data.get("location", {}).get("latitude") else 70
                
                # Determine data sources used
                sources = []
                if property_data.get("data_sources", {}).get("openstreetmap"):
                    sources.append("OpenStreetMap")
                if property_data.get("data_sources", {}).get("census"):
                    sources.append("US Census")
                if property_data.get("data_sources", {}).get("hud"):
                    sources.append("HUD Fair Market Rents")
                
                return {
                    "property_data": formatted_data,
                    "confidence_score": confidence,
                    "data_sources": sources or ["Enhanced Property Intelligence"],
                    "data_quality": {
                        "is_estimated_data": True,
                        "is_free_data": True,
                        "confidence": confidence,
                        "sources": sources,
                        "last_updated": "2025-10-03",
                        "notes": "Enhanced estimates from public data sources and market intelligence"
                    }
                }
            
            # Last resort: Basic property estimation for valid addresses
            self.logger.info(f"Generating basic property estimates for: {address}")
            
            # Parse location from address for basic estimates
            location_parts = address.split(",")
            city = location_parts[1].strip() if len(location_parts) > 1 else "Unknown"
            state = location_parts[2].strip().split()[0] if len(location_parts) > 2 else "Unknown"
            
            # Generate basic estimates based on location (with AI enhancement)
            basic_estimates = await self._generate_basic_estimates(address, city, state)
            
            return {
                "property_data": basic_estimates,
                "confidence_score": 70,  # Increased confidence with AI enhancement
                "data_sources": ["Property Intelligence Engine", "AI Analysis"],
                "data_quality": {
                    "is_estimated_data": True,
                    "is_free_data": True,
                    "confidence": 70,
                    "sources": ["Market Analysis", "AI Analysis"],
                    "last_updated": "2025-10-03",
                    "notes": "AI-enhanced property estimates with neighborhood and walkability analysis"
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching property data: {e}")
            
            # Even on error, try to provide basic estimates
            try:
                location_parts = address.split(",")
                city = location_parts[1].strip() if len(location_parts) > 1 else "Unknown"
                state = location_parts[2].strip().split()[0] if len(location_parts) > 2 else "Unknown"
                
                basic_estimates = await self._generate_basic_estimates(address, city, state)
                
                return {
                    "property_data": basic_estimates,
                    "confidence_score": 55,  # Slightly higher with AI fallback
                    "data_sources": ["Fallback Estimates", "AI Analysis"],
                    "data_quality": {
                        "is_estimated_data": True,
                        "is_free_data": True,
                        "confidence": 55,
                        "sources": ["Basic Market Analysis", "AI Fallback"],
                        "last_updated": "2025-10-03",
                        "notes": f"AI-enhanced fallback estimates due to data source issues: {str(e)}"
                    }
                }
            except:
                # Ultimate fallback
                raise HTTPException(
                    status_code=500,
                    detail=f"Unable to fetch property data for {address}. Error: {str(e)}"
                )
    
    def _get_basic_property_estimates(self, address: str, force_estimation: bool = False) -> Optional[Dict[str, Any]]:
        """
        Generate basic property estimates for fallback when no real data available
        """
        try:
            # Parse location from address for basic estimates
            location_parts = address.split(",")
            city = location_parts[1].strip() if len(location_parts) > 1 else "Unknown"
            state = location_parts[2].strip().split()[0] if len(location_parts) > 2 else "Unknown"
            
            # Generate basic estimates based on location
            basic_estimates = self._generate_basic_estimates(address, city, state)
            
            return {
                "property_type": basic_estimates.get("property_type", "Residential"),
                "units": basic_estimates.get("units", 1),
                "square_footage": basic_estimates.get("building_area_sqft", 1800),
                "year_built": basic_estimates.get("year_built", 1990),
                "estimated_value": int(basic_estimates.get("asking_price", "0").replace("$", "").replace(",", "")) if basic_estimates.get("asking_price") else 500000,
                "price_per_unit": 0,
                "price_per_sqft": 0,
                "data_quality": {
                    "is_estimated_data": True,
                    "confidence": 60,
                    "sources": ["Address Analysis"],
                    "notes": "Basic estimates from address analysis"
                }
            }
        except Exception as e:
            self.logger.error(f"Error generating basic estimates: {e}")
            return None

    async def _get_gemini_property_estimation(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Use Gemini AI to generate realistic neighborhood info and walk scores
        """
        try:
            if not self.gemini_model:
                self.logger.warning("Gemini AI not configured - using fallback data")
                return self._get_fallback_neighborhood_data(address)

            # Create a prompt for realistic neighborhood and walkability data
            prompt = f"""
You are a real estate data analyst. For the address: {address}

Generate realistic and accurate information for:

1. NEIGHBORHOOD NAME: What neighborhood/district is this address in?
2. WALK SCORE: Rate walkability from 0-100 based on the area (0=Car-Dependent, 50=Somewhat Walkable, 70=Very Walkable, 90+=Walker's Paradise)
3. NEIGHBORHOOD DESCRIPTION: Brief 2-3 sentence description of the area

Consider:
- The actual location and geography
- Typical amenities and businesses in the area
- Public transportation access
- Proximity to schools, shops, restaurants
- Urban density and development

Respond in this exact JSON format:
{{
    "neighborhood": "Neighborhood Name",
    "walk_score": 75,
    "neighborhood_description": "Brief description of the area's character and amenities.",
    "walkability_notes": "Explanation of walk score (e.g., 'Close to Metro stations and shopping centers')"
}}

Be realistic and accurate based on the actual location. Do not make up fake places.
"""

            response = self.gemini_model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Try to extract JSON from the response
            import json
            import re
            
            # Find JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                ai_data = json.loads(json_str)
                
                self.logger.info(f"Generated AI neighborhood data for: {address}")
                return {
                    "neighborhood": ai_data.get("neighborhood", "Unknown"),
                    "walk_score": min(100, max(0, ai_data.get("walk_score", 50))),  # Ensure 0-100 range
                    "neighborhood_description": ai_data.get("neighborhood_description", ""),
                    "walkability_notes": ai_data.get("walkability_notes", ""),
                    "data_source": "AI Analysis (Gemini)",
                    "confidence": 75
                }
            else:
                self.logger.warning("Could not parse AI response - using fallback")
                return self._get_fallback_neighborhood_data(address)
                
        except Exception as e:
            self.logger.error(f"Gemini AI error: {e}")
            return self._get_fallback_neighborhood_data(address)

    def _get_fallback_neighborhood_data(self, address: str) -> Dict[str, Any]:
        """
        Generate intelligent fallback neighborhood data when AI is not available
        """
        # Parse address for location intelligence
        address_lower = address.lower()
        
        # Known neighborhood mappings for major cities
        neighborhood_map = {
            # Los Angeles neighborhoods
            "hollywood": {"neighborhood": "Hollywood", "walk_score": 85, "description": "Entertainment district with theaters, restaurants, and nightlife"},
            "west hollywood": {"neighborhood": "West Hollywood", "walk_score": 88, "description": "Trendy area known for dining, shopping, and LGBTQ+ culture"},
            "beverly hills": {"neighborhood": "Beverly Hills", "walk_score": 75, "description": "Upscale residential and shopping district"},
            "santa monica": {"neighborhood": "Santa Monica", "walk_score": 90, "description": "Beachside community with pier, promenade, and bike paths"},
            "venice": {"neighborhood": "Venice", "walk_score": 85, "description": "Bohemian beach community with boardwalk and artistic culture"},
            "downtown": {"neighborhood": "Downtown LA", "walk_score": 82, "description": "Urban core with high-rises, arts district, and business center"},
            "encino": {"neighborhood": "Encino", "walk_score": 55, "description": "Suburban San Fernando Valley community with family-friendly atmosphere"},
            "pasadena": {"neighborhood": "Pasadena", "walk_score": 70, "description": "Historic city with Rose Bowl, museums, and Old Town shopping"},
            
            # San Francisco neighborhoods
            "san francisco": {"neighborhood": "San Francisco", "walk_score": 86, "description": "Dense urban environment with excellent public transit"},
            
            # Other major cities
            "manhattan": {"neighborhood": "Manhattan", "walk_score": 89, "description": "Urban center with subway access and walkable streets"},
            "chicago": {"neighborhood": "Chicago", "walk_score": 77, "description": "Midwest metropolis with public transit and urban amenities"},
            "austin": {"neighborhood": "Austin", "walk_score": 65, "description": "Texas capital known for music, tech, and food scene"},
        }
        
        # Find matching neighborhood
        neighborhood_data = None
        for key, data in neighborhood_map.items():
            if key in address_lower:
                neighborhood_data = data
                break
        
        # Default data if no match found
        if not neighborhood_data:
            # Determine walk score based on address characteristics
            if any(word in address_lower for word in ["blvd", "boulevard", "avenue", "ave"]):
                walk_score = 65  # Major streets tend to be more walkable
            elif any(word in address_lower for word in ["dr", "drive", "ct", "court", "way"]):
                walk_score = 45  # Residential streets tend to be less walkable
            else:
                walk_score = 55  # Default moderate walkability
            
            # Extract city from address
            parts = address.split(",")
            city = parts[1].strip() if len(parts) > 1 else "Unknown Area"
            
            neighborhood_data = {
                "neighborhood": city,
                "walk_score": walk_score,
                "description": f"Residential area in {city} with moderate walkability"
            }
        
        return {
            "neighborhood": neighborhood_data["neighborhood"],
            "walk_score": neighborhood_data["walk_score"],
            "neighborhood_description": neighborhood_data["description"],
            "walkability_notes": f"Walk Score {neighborhood_data['walk_score']}/100 - {self._get_walkability_label(neighborhood_data['walk_score'])}",
            "data_source": "Location Intelligence",
            "confidence": 70
        }
    
    def _get_walkability_label(self, score: int) -> str:
        """Convert walk score to descriptive label"""
        if score >= 90:
            return "Walker's Paradise"
        elif score >= 70:
            return "Very Walkable" 
        elif score >= 50:
            return "Somewhat Walkable"
        elif score >= 25:
            return "Car-Dependent"
        else:
            return "Car-Dependent"

    async def get_property_comps(self, address: str, radius_miles: float = 1.0) -> List[Dict[str, Any]]:
        """Get comparable properties in the area - ONLY real data, no mock data"""
        try:
            # Only return real comparable data if available
            # No mock/dummy data allowed
            self.logger.info(f"No comparable data source configured for: {address}")
            return []
        except Exception as e:
            self.logger.error(f"Error fetching property comps: {e}")
            return []

    async def _generate_basic_estimates(self, address: str, city: str, state: str) -> Dict[str, Any]:
        """
        Generate basic property estimates with AI-enhanced neighborhood data
        """
        # Property type detection
        address_lower = address.lower()
        if any(word in address_lower for word in ['apt', 'unit', 'ste', 'suite']):
            property_type = "Apartment"
            units = 1
            square_footage = 900
        elif any(word in address_lower for word in ['blvd', 'avenue', 'street']):
            property_type = "Residential"
            units = 1
            square_footage = 1800
        else:
            property_type = "Residential"
            units = 1
            square_footage = 1500
        
        # Year built estimation
        year_built = 1990
        
        # Get AI neighborhood data
        neighborhood_data = await self._get_gemini_property_estimation(address)
        
        # Market-based pricing by location
        city_multipliers = {
            'los angeles': 3.5, 'la': 3.5, 'beverly hills': 5.0, 'santa monica': 4.5,
            'west hollywood': 4.0, 'hollywood': 3.0, 'pasadena': 2.5, 'glendale': 2.3,
            'san francisco': 4.5, 'san jose': 3.5, 'oakland': 2.8, 'berkeley': 3.2,
            'new york': 4.0, 'manhattan': 5.5, 'brooklyn': 3.5, 'queens': 2.8,
            'chicago': 2.2, 'miami': 2.8, 'boston': 3.0, 'seattle': 3.2, 'austin': 2.5
        }
        
        multiplier = 1.0
        city_lower = city.lower()
        for city_name, mult in city_multipliers.items():
            if city_name in city_lower:
                multiplier = mult
                break
        
        # California gets higher baseline
        if state.upper() == "CA" and multiplier == 1.0:
            multiplier = 2.0
        
        # Calculate estimates
        base_rent = 1200 * multiplier
        estimated_value = int(base_rent * 200)  # 200x monthly rent
        
        return {
            "address": address,
            "property_type": property_type,
            "units": units,
            "building_area_sqft": square_footage,
            "year_built": year_built,
            "asking_price": f"${estimated_value:,}",
            "estimated_rent": f"${int(base_rent):,}/month",
            "neighborhood": neighborhood_data.get("neighborhood", f"{city}, {state}"),
            "walk_score": neighborhood_data.get("walk_score", 50),
            "walkability_notes": neighborhood_data.get("walkability_notes", ""),
            "neighborhood_description": neighborhood_data.get("neighborhood_description", "")
        }

    def _validate_address_format(self, address: str) -> str:
        """
        Validate address format to ensure it has necessary components
        Returns error message if invalid, empty string if valid
        """
        import re
        
        address = address.strip()
        
        # Check if address has a house number (digits followed by space)
        if not re.match(r'^\d+\s+', address):
            return "Address must include a house number (e.g., '123 Main St, City, State ZIP')"
        
        # Check for basic components (should have at least 2 commas for city, state)
        parts = address.split(',')
        if len(parts) < 3:
            return "Please include complete address: street, city, state, and ZIP code"
        
        # Check for state and ZIP in last part
        last_part = parts[-1].strip()
        if not re.search(r'\b[A-Z]{2}\s+\d{5}', last_part):
            return "Please include state and ZIP code (e.g., 'CA 90210')"
        
        return ""  # Valid address
