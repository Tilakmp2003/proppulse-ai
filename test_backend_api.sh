#!/bin/bash

echo "Testing PropPulse Backend API with different property types"
echo "=========================================================="
echo

API_URL="https://proppulse-ai-production.up.railway.app"

# Function to test an address
test_address() {
    local address="$1"
    local address_type="$2"
    
    echo "Testing $address_type address: $address"
    echo "-----------------------------------------"
    
    # Use curl to call the quick-analysis endpoint
    curl -s -X POST "$API_URL/quick-analysis" \
        -H "Content-Type: application/json" \
        -d "{\"address\": \"$address\"}" | jq '{
            property_type: .analysis_result.property_details.property_type,
            units: .analysis_result.property_details.units,
            square_footage: .analysis_result.property_details.square_footage,
            market_value: .analysis_result.property_details.market_value,
            data_quality: .analysis_result.market_data.data_quality
        }'
    
    echo
    echo
}

# Test single family home
test_address "123 Main St, Austin, TX 78701" "Single Family"

# Test commercial property
test_address "789 Office Plaza, Dallas, TX 75201" "Commercial" 

# Test multifamily property
test_address "Wilshire Plaza, 5678 Wilshire Blvd, Los Angeles, CA 90036" "Multifamily"

echo "Testing complete!"
