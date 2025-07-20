# BACKEND CHANGES NEEDED

## 1. Update the \_get_basic_property_estimates method in external_apis.py

Change this:

```python
def _get_basic_property_estimates(self, address: str) -> Optional[Dict[str, Any]]:
```

To this:

```python
def _get_basic_property_estimates(self, address: str, force_estimation: bool = False) -> Optional[Dict[str, Any]]:
```

And change this condition:

```python
if is_likely_multifamily or has_unit_number:
```

To this:

```python
if is_likely_multifamily or has_unit_number or force_estimation:
```

Before the return None line, add this:

```python
            elif force_estimation:
                # For non-multifamily addresses with force_estimation
                if 'commercial' in address_lower or 'business' in address_lower or 'office' in address_lower or 'plaza' in address_lower:
                    property_type = "Commercial"
                    estimated_units = 1
                    estimated_sqft = 5000  # Conservative commercial estimate
                    estimated_value = estimated_sqft * 250  # $250 per sqft
                else:
                    property_type = "Single Family"
                    estimated_units = 1
                    estimated_sqft = 2000  # Average single family home
                    estimated_value = 450000  # Conservative home value
```

## 2. Update the quick-analysis endpoint in main.py

Replace this:

```python
        # DIRECT SMART ESTIMATION CHECK: Check if address is likely multifamily first
        is_multifamily = any(indicator in address.lower() for indicator in ['apt', 'apartment', 'unit', 'suite', '#', 'complex', 'towers', 'plaza'])

        # If it looks like multifamily, try to use the smart estimation directly
        if is_multifamily:
            print(f"Detected multifamily address: {address} - using smart estimation")
            estimated_data = external_api_service._get_basic_property_estimates(address)
            if estimated_data:
                # We have estimation data - use it directly
                property_data = estimated_data
            else:
                # Fall back to regular process if estimation failed
                property_data = await external_api_service.get_property_data(address)
        else:
            # Regular flow for non-multifamily addresses
            property_data = await external_api_service.get_property_data(address)
```

With this:

```python
        # Check if address has multifamily indicators (for data quality flag)
        is_multifamily = any(indicator in address.lower() for indicator in ['apt', 'apartment', 'unit', 'suite', '#', 'complex', 'towers', 'plaza'])

        # First try to get real property data
        property_data = await external_api_service.get_property_data(address)

        # Check if we got meaningful data - if not, use smart estimation for ALL addresses
        has_meaningful_data = property_data.get("property_type") != "Unknown" or property_data.get("units", 0) > 0

        if not has_meaningful_data:
            print(f"No meaningful data for: {address} - using smart estimation")
            estimated_data = external_api_service._get_basic_property_estimates(address, force_estimation=True)
            if estimated_data:
                # We have estimation data - use it directly
                property_data = estimated_data
```

And replace this in the market_data section:

```python
                    "data_quality": property_data.get("data_quality", {}) or {
                        "is_estimated_data": is_multifamily,
                        "confidence": 25 if is_multifamily else None,
                        "sources": ["Address Analysis"] if is_multifamily else None,
                        "notes": "⚠️ ESTIMATES ONLY - Based on address analysis" if is_multifamily else None
                    }
```

With this:

```python
                    "data_quality": property_data.get("data_quality", {}) or {
                        "is_estimated_data": True,  # Always mark as estimated if we had to fallback
                        "confidence": 25,  # Low confidence
                        "sources": ["Address Analysis"],
                        "notes": "⚠️ ESTIMATES ONLY - Based on address analysis when real data unavailable"
                    }
```

## 3. No changes needed to frontend, it's already using the right property names (is_estimated_data)
