#!/bin/bash

# Test the quick-analysis endpoint with updated code (no default values)
echo "Testing quick-analysis endpoint..."

# Address to test
ADDRESS="5678, Wilshire Boulevard, Miracle Mile, Mid-Wilshire, Los Angeles, Los Angeles County, California, 90036, United States"

# API URL
API_URL="https://proppulse-ai-production.up.railway.app"

# Make the API request
curl -X POST \
  -H "Content-Type: application/json" \
  -d "{\"address\": \"$ADDRESS\"}" \
  $API_URL/quick-analysis | jq .

echo ""
echo "Test complete!"
