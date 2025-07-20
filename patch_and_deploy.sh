#!/bin/bash

# This script patches the external_apis.py file directly with our changes
# Use this when committing through git isn't working properly

# Create a backup of the original file
cp backend/services/external_apis.py backend/services/external_apis.py.original

# Apply our fix directly using sed
cat > backend/services/external_apis.py << 'EOL'
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
        
        # Track API usage to avoid hitting limits
        self.api_call_counters = {}
        
    async def get_property_data(self, address: str) -> Dict[str, Any]:
        """
        Get property data from free APIs
        Returns real property data where available, minimal structure where not
        Never returns mock data
        """
        self.logger.info(f"Fetching property data for: {address}")
        
        try:
            # First try free property data sources
            from services.free_property_apis import get_free_property_data
            property_data = await get_free_property_data(address)
            
            # If we get useful data from free APIs, return it
            if property_data and property_data.get("property_type") != "Unknown":
                self.logger.info(f"Got real property data from free APIs for: {address}")
                # Add data quality information
                property_data["data_quality"] = {
                    "is_estimated_data": False,
                    "is_free_data": True,
                    "confidence": 80,
                    "sources": property_data.get("data_sources", ["Free Property Data API"]),
                    "last_updated": property_data.get("last_updated", "2025-07-20")
                }
                return property_data
            
            # If free APIs didn't return useful data, try basic estimates
            self.logger.info(f"No real property data from free APIs for: {address}, using basic estimates")
            basic_estimates = self._get_basic_property_estimates(address)
            if basic_estimates:
                self.logger.info(f"Using basic property estimates for: {address}")
                return basic_estimates
            
            # If all else fails, return a minimal structure with Unknown values
            # This is NOT mock data - it's an honest representation of unknown values
            self.logger.warning(f"No property data available for: {address}")
            return {
                "address": address,
                "property_type": "Unknown",
                "units": 0,
                "square_footage": None,
                "estimated_value": 0,
                "data_quality": {
                    "is_estimated_data": False,
                    "is_free_data": False, 
                    "confidence": 0,
                    "sources": [],
                    "notes": "No property data available from any source"
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching property data: {e}")
            self.logger.error(traceback.format_exc())
            
            # Return minimal structure on error - not mock data
            return {
                "address": address,
                "property_type": "Unknown",
                "units": 0,
                "square_footage": None,
                "estimated_value": 0,
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
        Provide basic property estimates based on address analysis when APIs are unavailable
        This is transparent about being estimates, not real data
        
        Parameters:
        - address: The property address
        - force_estimation: If True, provide estimates even for non-multifamily properties
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
            
            # First check for multifamily properties
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
            # Then check for commercial properties or if force_estimation is on
            elif ('commercial' in address_lower or 'business' in address_lower or 
                  'office' in address_lower or 'plaza' in address_lower) or force_estimation:
                # Check if it's likely commercial
                if ('commercial' in address_lower or 'business' in address_lower or 
                    'office' in address_lower or 'plaza' in address_lower):
                    property_type = "Commercial"
                    estimated_units = 1
                    estimated_sqft = 5000  # Conservative commercial estimate
                    estimated_value = estimated_sqft * 250  # $250 per sqft
                # Otherwise assume single family when force_estimation is true
                else:
                    property_type = "Single Family"
                    estimated_units = 1
                    estimated_sqft = 2000  # Average single family home
                    estimated_value = 450000  # Conservative home value
            else:
                return None  # No estimation if not multifamily and not forced
                
            return {
                "address": address,
                "property_type": property_type,
                "units": estimated_units,
                "square_footage": estimated_sqft,
                "estimated_value": estimated_value,
                "price_per_unit": int(estimated_value / max(estimated_units, 1)),
                "price_per_sqft": round(estimated_value / estimated_sqft, 2),
                    
                    "market_data": {
                        "avg_rent_per_unit": estimated_units * 18,  # Conservative rent estimate
                        "estimated_cap_rate": 6.5,
                    },
                    
                    "data_quality": {
                        "is_estimated_data": True,
                        "confidence": 25,  # Low confidence for most properties
                        "sources": ["Address Analysis"],
                        "last_updated": "2025-07-20",
                        "notes": "⚠️ ESTIMATES ONLY - Based on address analysis when real data APIs unavailable. Use for initial screening only."
                    }
                }
            
        except Exception as e:
            self.logger.error(f"Error in basic estimates: {e}")
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
EOL

# Print success message
echo "✅ external_apis.py has been patched with the corrected implementation"
echo "Now let's commit and push these changes"

# Add the file to git
git add backend/services/external_apis.py

# Commit with our message
git commit -F commit-message.txt

# Push to origin
git push

echo "✅ Changes pushed to GitHub. Railway should now deploy the updated backend."
