#!/bin/bash

# Display what we're going to do
echo "Committing changes to external_apis.py and deploying to Railway"

# Stage the specific file we changed
git add backend/services/external_apis.py DEPLOYMENT_FIX.md

# Commit with our prepared message
git commit -F commit-message.txt

# Push to the repository (assuming main branch and Railway auto-deploys)
git push origin main

echo "Changes pushed to repository."
echo "Railway should automatically deploy the updated backend."
echo ""
echo "After deployment, test the frontend with different property types:"
echo "- Single-family (e.g., '123 Main St, Anytown USA')"
echo "- Commercial (e.g., '123 Office Plaza, Business District')"
echo "- Multifamily (e.g., 'Wilshire Apartment Complex, Los Angeles')"
echo ""
echo "All properties should now show estimated data when real data isn't available,"
echo "properly marked with the 'Estimated Data' badge."
