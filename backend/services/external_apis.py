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
                
                # Format the data to match frontend expectations
                formatted_data = {
                    "address": property_data.get("address", address),
                    "property_type": property_data.get("property_type", "Residential"),
                    "units": property_data.get("units", 1),
                    "building_area_sqft": property_data.get("square_footage"),
                    "year_built": property_data.get("year_built"),
                    "neighborhood": property_data.get("location", {}).get("display_name", "").split(",")[1:3],
                    "walk_score": "Not available"
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
            
            # Generate basic estimates based on location
            basic_estimates = self._generate_basic_estimates(address, city, state)
            
            return {
                "property_data": basic_estimates,
                "confidence_score": 60,
                "data_sources": ["Property Intelligence Engine"],
                "data_quality": {
                    "is_estimated_data": True,
                    "is_free_data": True,
                    "confidence": 60,
                    "sources": ["Market Analysis"],
                    "last_updated": "2025-10-03",
                    "notes": "Basic property estimates based on location and market analysis"
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching property data: {e}")
            
            # Even on error, try to provide basic estimates
            try:
                location_parts = address.split(",")
                city = location_parts[1].strip() if len(location_parts) > 1 else "Unknown"
                state = location_parts[2].strip().split()[0] if len(location_parts) > 2 else "Unknown"
                
                basic_estimates = self._generate_basic_estimates(address, city, state)
                
                return {
                    "property_data": basic_estimates,
                    "confidence_score": 50,
                    "data_sources": ["Fallback Estimates"],
                    "data_quality": {
                        "is_estimated_data": True,
                        "is_free_data": True,
                        "confidence": 50,
                        "sources": ["Basic Market Analysis"],
                        "last_updated": "2025-10-03",
                        "notes": f"Fallback estimates due to data source issues: {str(e)}"
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
        REMOVED: No estimates allowed - only real ATTOM data
        """
        self.logger.warning(f"Property estimation disabled - only real data allowed for: {address}")
        return None

    async def _get_gemini_property_estimation(self, address: str) -> Optional[Dict[str, Any]]:
        """
        REMOVED: No AI estimates allowed - only real verified data
        """
        self.logger.warning(f"AI estimation disabled - only real data allowed for: {address}")
        return None

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

    def _generate_basic_estimates(self, address: str, city: str, state: str) -> Dict[str, Any]:
        """
        Generate basic property estimates based on location and address analysis
        """
        # Default values
        property_type = "Residential"
        units = 1
        square_footage = 1800
        year_built = 1990
        
        # Analyze address for property type hints
        address_lower = address.lower()
        
        # Check for multifamily indicators
        multifamily_keywords = ['apartment', 'apt', 'unit', 'complex', 'plaza', 'towers', 'residences']
        if any(keyword in address_lower for keyword in multifamily_keywords):
            property_type = "Multifamily"
            units = 24
            square_footage = units * 850
        
        # Check for commercial indicators
        commercial_keywords = ['office', 'commercial', 'retail', 'store', 'building', 'center']
        if any(keyword in address_lower for keyword in commercial_keywords):
            property_type = "Commercial"
            units = 1
            square_footage = 5000
        
        # Location-based adjustments
        city_multipliers = {
            "los angeles": 2.8, "hollywood": 2.6, "west hollywood": 3.2,
            "beverly hills": 4.5, "santa monica": 3.8, "venice": 3.0,
            "san francisco": 4.8, "san diego": 2.6, "encino": 2.0
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
            "neighborhood": f"{city}, {state}",
            "walk_score": "Not available"
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
