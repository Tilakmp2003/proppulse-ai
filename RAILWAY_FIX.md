"""
MANUAL FIX FOR RAILWAY DEPLOYMENT

This file contains the corrected version of the \_get_basic_property_estimates method
from external_apis.py. Copy this entire method and replace the existing one in
the Railway deployment.

You can do this through Railway's web console:

1. Go to the Railway dashboard
2. Open your PropPulse project
3. Select the backend service
4. Click on "Shell" tab
5. Use the nano editor: nano backend/services/external_apis.py
6. Find the \_get_basic_property_estimates method and replace it with this one
7. Save the file (Ctrl+O, Enter, Ctrl+X)
8. The service should automatically restart with the new code
   """

def \_get_basic_property_estimates(self, address: str, force_estimation: bool = False) -> Optional[Dict[str, Any]]:
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
