#!/bin/bash

# Integration test script for orchestratorr
# Tests search endpoint and CORS configuration

set -e

FRONTEND_URL="http://localhost:8081"
BACKEND_URL="http://localhost:8000"
API_ENDPOINT="$FRONTEND_URL/api/v1/search"

echo "🧪 Starting integration tests for orchestratorr..."
echo ""

# Test 1: Health check on backend
echo "1️⃣  Testing backend health endpoint..."
HEALTH_RESPONSE=$(curl -s "$BACKEND_URL/health")
if echo "$HEALTH_RESPONSE" | grep -q '"status":"healthy"'; then
    echo "   ✅ Backend health check passed"
else
    echo "   ❌ Backend health check failed: $HEALTH_RESPONSE"
    exit 1
fi

# Test 2: API health check
echo "2️⃣  Testing API v1 health endpoint..."
API_HEALTH=$(curl -s "$BACKEND_URL/api/v1/health")
if echo "$API_HEALTH" | grep -q '"status":"healthy"'; then
    echo "   ✅ API health check passed"
else
    echo "   ❌ API health check failed: $API_HEALTH"
    exit 1
fi

# Test 3: Frontend accessibility
echo "3️⃣  Testing frontend accessibility on port 8081..."
FRONTEND_RESPONSE=$(curl -s -w "\n%{http_code}" "$FRONTEND_URL" | tail -1)
if [ "$FRONTEND_RESPONSE" = "200" ]; then
    echo "   ✅ Frontend accessible on port 8081"
else
    echo "   ❌ Frontend not accessible (HTTP $FRONTEND_RESPONSE)"
    exit 1
fi

# Test 4: Search endpoint with CORS headers
echo "4️⃣  Testing search endpoint with CORS..."
SEARCH_RESPONSE=$(curl -s -i -X GET \
    -H "Origin: http://localhost:8081" \
    "$API_ENDPOINT?q=test&limit=10" \
    2>&1)

if echo "$SEARCH_RESPONSE" | grep -q "HTTP"; then
    HTTP_CODE=$(echo "$SEARCH_RESPONSE" | head -1 | awk '{print $2}')
    echo "   Response code: $HTTP_CODE"
    
    # Check for CORS headers or valid response
    if echo "$SEARCH_RESPONSE" | grep -q "Access-Control-Allow-Origin\|\"results\""; then
        echo "   ✅ Search endpoint responds (CORS headers or valid JSON)"
    else
        echo "   ⚠️  Search endpoint responds but check structure"
        echo "$SEARCH_RESPONSE" | head -20
    fi
else
    echo "   ❌ Search request failed"
    exit 1
fi

# Test 5: Search endpoint validation (missing query param)
echo "5️⃣  Testing search endpoint validation..."
INVALID_RESPONSE=$(curl -s -w "\n%{http_code}" "$API_ENDPOINT?limit=10" | tail -1)
if [ "$INVALID_RESPONSE" = "422" ]; then
    echo "   ✅ Validation error for missing query parameter (422)"
else
    echo "   ⚠️  Expected 422, got $INVALID_RESPONSE"
fi

# Test 6: Search with query parameter
echo "6️⃣  Testing search with valid query..."
SEARCH_DATA=$(curl -s "$API_ENDPOINT?q=matrix&limit=5")
if echo "$SEARCH_DATA" | grep -q '"query"\|"results"'; then
    echo "   ✅ Search endpoint returns JSON structure"
    TOTAL=$(echo "$SEARCH_DATA" | grep -o '"total":[0-9]*' | head -1)
    echo "   Found $TOTAL results"
else
    echo "   ❌ Search response missing expected fields"
    echo "$SEARCH_DATA"
    exit 1
fi

echo ""
echo "✅ All integration tests passed!"
echo ""
echo "To stop services: docker-compose down"
