#!/bin/bash

# Test the quick-analysis endpoint
echo "Testing quick-analysis endpoint..."

# Replace with the actual address you're testing
ADDRESS="1234 Commerce St, Austin, TX 78701"

# Make the API request
curl -X POST \
  -H "Content-Type: application/json" \
  -d "{\"address\": \"$ADDRESS\"}" \
  http://localhost:8000/quick-analysis | jq

echo "Test complete!"
