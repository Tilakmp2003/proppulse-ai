"""
Temporary fix file for main.py quick-analysis endpoint
"""

# Quick analysis endpoint - modified to use smart estimation for all properties
@app.post("/quick-analysis")
async def quick_property_analysis(request: dict):
    """
    Quick property analysis using only free APIs - no file upload required
    Returns real property data from free sources for immediate display
    """
    try:
        address = request.get("address", "").strip()
        if not address:
            raise HTTPException(status_code=400, detail="Address is required")
        
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
        
        # Create a simplified analysis result for quick display
        quick_result = {
            "id": f"quick-{str(uuid.uuid4())[:8]}",
            "property_address": address,
            "analysis_result": {
                "pass_fail": "PENDING",  # Quick analysis doesn't include pass/fail
                "score": 0,  # No score for quick analysis
                "property_details": {
                    "property_type": property_data.get("property_type", "Unknown"),
                    "year_built": property_data.get("year_built"),
                    "units": property_data.get("units", 0),
                    "square_footage": property_data.get("square_footage"),
                    "lot_size": property_data.get("lot_size"),
                    "market_value": property_data.get("estimated_value", 0),
                    "price_per_unit": property_data.get("price_per_unit", 0),
                    "price_per_sqft": property_data.get("price_per_sqft", 0),
                },
                "market_data": {
                    # Include market data from property data
                    **(property_data.get("market_data", {})),
                    # Always include data quality information
                    "data_quality": property_data.get("data_quality", {}) or {
                        "is_estimated_data": True,  # Always mark as estimated if we had to fallback
                        "confidence": 25,  # Low confidence
                        "sources": ["Address Analysis"],
                        "notes": "⚠️ ESTIMATES ONLY - Based on address analysis when real data unavailable"
                    }
                },
                "neighborhood_info": property_data.get("neighborhood_data", {}),
                "neighborhood_data": property_data.get("neighborhood_data", {}),
                "demographics": property_data.get("demographics", {}),
                "location_info": property_data.get("location_info", {}),
                "data_sources": property_data.get("data_sources", []),
                "ai_analysis": "Quick property lookup using free data sources. Upload financial documents for comprehensive analysis.",
            },
            "created_at": datetime.utcnow().isoformat(),
            "analysis_type": "quick_lookup"
        }
        
        return quick_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick analysis failed: {str(e)}")
