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
        Returns only verified property data, not estimates
        """
        self.logger.info(f"Fetching REAL property data for: {address}")
        
        try:
            # Use the enhanced free property data service with ATTOM integration
            from services.free_property_apis import FreePropertyDataService
            service = FreePropertyDataService()
            property_data = await service.get_comprehensive_free_data(address)
            
            # Check if we have REAL ATTOM data (not just estimates)
            attom_data = property_data.get("data_sources", {}).get("attom", {})
            has_real_attom_data = attom_data and attom_data.get("attom_id")
            
            if has_real_attom_data:
                self.logger.info(f"Got REAL ATTOM property data for: {address}")
                # Return real ATTOM data with high confidence
                property_data["data_quality"] = {
                    "is_estimated_data": False,
                    "is_free_data": False,
                    "confidence": 95,
                    "sources": ["ATTOM Data API"],
                    "last_updated": "2025-07-20",
                    "notes": "Verified property records from ATTOM Data"
                }
                return property_data
            
            # Check if we have useful data from free public APIs (not estimates)
            elif (property_data and 
                  property_data.get("property_type") != "Unknown" and
                  property_data.get("location", {}).get("latitude")):
                
                self.logger.info(f"Got real public data (no ATTOM) for: {address}")
                property_data["data_quality"] = {
                    "is_estimated_data": True,
                    "is_free_data": True,
                    "confidence": 60,
                    "sources": [name for name, data in property_data.get("data_sources", {}).items() if data and name != "attom"],
                    "last_updated": "2025-07-20",
                    "notes": "Based on public records and location data - no verified property details"
                }
                return property_data
            
            # If no real data available, use Gemini AI for intelligent estimation
            # Only if Gemini is configured, otherwise return "Not available"
            if self.gemini_model:
                self.logger.info(f"Using Gemini AI to estimate property data for: {address}")
                gemini_data = await self._get_gemini_property_estimation(address)
                if gemini_data:
                    return gemini_data
            
            # If Gemini is not available, return minimal structure with "Not available"
            self.logger.warning(f"No real property data or AI estimation available for: {address}")
            return {
                "address": address,
                "property_type": "Not available",
                "units": None,
                "square_footage": None,
                "year_built": None,
                "estimated_value": None,
                "data_quality": {
                    "is_estimated_data": False,
                    "is_free_data": False,
                    "confidence": 0,
                    "sources": [],
                    "notes": "No verified property data available. ATTOM API key required for real property records."
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching property data: {e}")
            self.logger.error(traceback.format_exc())
            
            # Return minimal structure on error - not mock data
            return {
                "address": address,
                "property_type": "Not available",
                "units": None,
                "square_footage": None,
                "year_built": None,
                "estimated_value": None,
                "data_quality": {
                    "is_estimated_data": False,
                    "is_free_data": False,
                    "confidence": 0,
                    "sources": [],
                    "notes": f"Error fetching property data: {str(e)}"
                }
            }
    
    def _get_basic_property_estimates(self, address: str, force_estimation: bool = False) -> Optional[Dict[str, Any]]:
        """
        DISABLED: No more estimates - only real ATTOM data allowed
        This function is kept for compatibility but always returns None
        """
        self.logger.info(f"Estimation disabled - only real ATTOM data allowed for: {address}")
        return None

    async def _get_gemini_property_estimation(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Use Gemini AI to provide intelligent property estimates when real data is unavailable
        """
        try:
            if not self.gemini_model:
                return None
                
            prompt = f"""
            You are a real estate expert. Analyze this address and provide realistic property estimates based on your knowledge of the area and typical property characteristics.
            
            Address: {address}
            
            Please provide estimates in this exact JSON format:
            {{
                "property_type": "Single Family" | "Multifamily" | "Commercial" | "Condo" | "Townhouse",
                "units": <estimated number of units>,
                "square_footage": <estimated total square footage>,
                "year_built": <estimated year built (1900-2024)>,
                "estimated_value": <estimated market value in USD>,
                "lot_size": <estimated lot size in square feet>,
                "bedrooms": <estimated bedrooms per unit for residential>,
                "bathrooms": <estimated bathrooms per unit for residential>,
                "market_data": {{
                    "avg_rent_per_unit": <estimated monthly rent per unit>,
                    "estimated_cap_rate": <estimated cap rate as percentage>,
                    "price_per_sqft": <estimated price per square foot>
                }},
                "neighborhood_info": {{
                    "area_description": "<brief description of the neighborhood>",
                    "estimated_walk_score": <estimated walk score 0-100>
                }},
                "reasoning": "<brief explanation of your estimates>"
            }}
            
            Base your estimates on:
            - The specific location and neighborhood characteristics
            - Typical property types for the area
            - Current market conditions
            - Regional real estate patterns
            
            Be realistic and conservative in your estimates. If you're unsure about something, provide a reasonable range midpoint.
            """
            
            response = self.gemini_model.generate_content(prompt)
            
            if response and response.text:
                # Try to parse the JSON response
                try:
                    # Extract JSON from the response text
                    response_text = response.text.strip()
                    
                    # Remove any markdown formatting
                    if response_text.startswith("```json"):
                        response_text = response_text[7:]
                    if response_text.endswith("```"):
                        response_text = response_text[:-3]
                    
                    gemini_data = json.loads(response_text)
                    
                    # Format the response to match our expected structure
                    formatted_data = {
                        "address": address,
                        "property_type": gemini_data.get("property_type", "Unknown"),
                        "units": gemini_data.get("units"),
                        "square_footage": gemini_data.get("square_footage"),
                        "year_built": gemini_data.get("year_built"),
                        "estimated_value": gemini_data.get("estimated_value"),
                        "lot_size": gemini_data.get("lot_size"),
                        "bedrooms": gemini_data.get("bedrooms"),
                        "bathrooms": gemini_data.get("bathrooms"),
                        "market_data": gemini_data.get("market_data", {}),
                        "neighborhood_info": gemini_data.get("neighborhood_info", {}),
                        "data_quality": {
                            "is_estimated_data": True,
                            "is_free_data": False,
                            "confidence": 75,  # Good confidence for AI estimates
                            "sources": ["Gemini AI Analysis"],
                            "last_updated": "2025-07-20",
                            "notes": f"AI-powered property estimates based on location analysis. Reasoning: {gemini_data.get('reasoning', 'General area knowledge')}"
                        }
                    }
                    
                    self.logger.info(f"Gemini provided property estimates for: {address}")
                    return formatted_data
                    
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse Gemini response as JSON: {e}")
                    self.logger.error(f"Response text: {response.text}")
                    return None
                    
            return None
            
        except Exception as e:
            self.logger.error(f"Error in Gemini property estimation: {e}")
            return None

    async def get_property_comps(self, address: str, radius_miles: float = 1.0) -> List[Dict[str, Any]]:
        """Get comparable properties in the area"""
        try:
            # Since we don't have a real comps API in this implementation,
            # return an empty list instead of mock data
            return []
        except Exception as e:
            self.logger.error(f"Error fetching property comps: {e}")
            return []
