#!/bin/bash

# Quick Backend Test for PropPulse AI

# Get Railway URL from user input or argument
if [ -z "$1" ]; then
    echo "🚀 PropPulse AI Backend Tester"
    echo "==============================="
    echo ""
    echo "Please enter your Railway URL from the dashboard:"
    read -p "Railway URL: " RAILWAY_URL
    
    if [ -z "$RAILWAY_URL" ]; then
        echo "❌ No URL provided. Exiting..."
        exit 1
    fi
else
    RAILWAY_URL="$1"
fi

echo ""
echo "🧪 Testing PropPulse AI Backend"
echo "URL: $RAILWAY_URL"
echo "================================"
echo ""

# Test 1: Health Check
echo "🔍 Test 1: Health Endpoint"
echo "Endpoint: $RAILWAY_URL/health"
response=$(curl -s -w "%{http_code}" "$RAILWAY_URL/health")
http_code="${response: -3}"

if [ "$http_code" = "200" ]; then
    echo "✅ Health check passed! (HTTP $http_code)"
    echo "Response: ${response%???}"
else
    echo "❌ Health check failed! (HTTP $http_code)"
    echo "Response: ${response%???}"
fi
echo ""

# Test 2: Root Endpoint
echo "🔍 Test 2: Root Endpoint"
echo "Endpoint: $RAILWAY_URL/"
response=$(curl -s -w "%{http_code}" "$RAILWAY_URL/")
http_code="${response: -3}"

if [ "$http_code" = "200" ]; then
    echo "✅ Root endpoint works! (HTTP $http_code)"
    echo "Response: ${response%???}"
else
    echo "❌ Root endpoint failed! (HTTP $http_code)"
    echo "Response: ${response%???}"
fi
echo ""

# Test 3: API Documentation
echo "🔍 Test 3: API Documentation"
echo "Endpoint: $RAILWAY_URL/openapi.json"
response=$(curl -s -w "%{http_code}" "$RAILWAY_URL/openapi.json")
http_code="${response: -3}"

if [ "$http_code" = "200" ]; then
    echo "✅ API schema available! (HTTP $http_code)"
else
    echo "❌ API schema failed! (HTTP $http_code)"
fi
echo ""

# Test 4: Interactive API Docs
echo "🔍 Test 4: Interactive API Documentation"
echo "Endpoint: $RAILWAY_URL/docs"
response=$(curl -s -w "%{http_code}" "$RAILWAY_URL/docs")
http_code="${response: -3}"

if [ "$http_code" = "200" ]; then
    echo "✅ API docs page available! (HTTP $http_code)"
else
    echo "❌ API docs page failed! (HTTP $http_code)"
fi
echo ""

echo "📖 Open these URLs in your browser:"
echo "   • 🏥 Health Check: $RAILWAY_URL/health"
echo "   • 📚 API Documentation: $RAILWAY_URL/docs"
echo "   • 📋 ReDoc Documentation: $RAILWAY_URL/redoc"
echo "   • 🔗 API Schema: $RAILWAY_URL/openapi.json"
echo ""

# Summary
echo "🎯 Summary:"
if curl -s "$RAILWAY_URL/health" > /dev/null; then
    echo "✅ Your backend is LIVE and responding!"
    echo "🎉 PropPulse AI API is ready for integration!"
else
    echo "❌ Backend seems to have issues"
    echo "🔧 Check Railway logs for details"
fi
echo ""
echo "🚀 Next steps:"
echo "   1. Test API endpoints in browser ($RAILWAY_URL/docs)"
echo "   2. Update frontend .env.local with this URL"
echo "   3. Deploy frontend to Vercel"
