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
        Get property data prioritizing ATTOM API for real data
        Returns ONLY verified real property data - NO ESTIMATES OR DUMMY DATA
        """
        self.logger.info(f"Fetching REAL property data for: {address}")
        
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
                    "address": address,
                    "property_type": attom_data.get("property_type", "Unknown"),
                    "units": attom_data.get("units") or 1,
                    "square_footage": attom_data.get("square_footage"),
                    "year_built": attom_data.get("year_built"),
                    "bedrooms": attom_data.get("bedrooms"),
                    "bathrooms": attom_data.get("bathrooms"),
                    "lot_size": attom_data.get("lot_size"),
                    "assessed_value": attom_data.get("assessed_value"),
                    "tax_amount": attom_data.get("tax_amount"),
                    "data_quality": {
                        "is_estimated_data": False,
                        "is_free_data": False,
                        "confidence": 95,
                        "sources": ["ATTOM Data API"],
                        "last_updated": "2025-10-02",
                        "notes": "Verified property records from ATTOM Data API"
                    }
                }
                
                # Get free data to supplement location info
                free_data = await service.get_comprehensive_free_data(address)
                if free_data.get("location"):
                    property_data["location"] = free_data["location"]
                
                return property_data
            
            # If no ATTOM data, try free APIs for basic location data
            property_data = await service.get_comprehensive_free_data(address)
            
            # Only return if we have REAL location data (not estimates)
            if (property_data and 
                property_data.get("location", {}).get("latitude") and
                property_data.get("location", {}).get("longitude")):
                
                self.logger.info(f"Got verified location data for: {address}")
                property_data["data_quality"] = {
                    "is_estimated_data": False,
                    "is_free_data": True,
                    "confidence": 85,
                    "sources": ["OpenStreetMap", "US Census"],
                    "last_updated": "2025-10-02",
                    "notes": "Verified location data from public sources"
                }
                return property_data
            
            # NO FALLBACK DATA - If we can't get real data, return error
            self.logger.warning(f"No real property data available for: {address}")
            raise HTTPException(
                status_code=404, 
                detail=f"No verified property data found for address: {address}. Please check the address and try again."
            )
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            self.logger.error(f"Error fetching property data: {e}")
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
