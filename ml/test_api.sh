#!/bin/bash

# Test script for Fraud Detection API
# Usage: ./test_api.sh [http://localhost:5000]

API_URL="${1:-http://localhost:5000}"

echo "================================"
echo "Fraud Detection API Test Script"
echo "================================"
echo "Testing API at: $API_URL"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check response
check_response() {
    local status=$1
    local expected=$2
    if [ "$status" -eq "$expected" ]; then
        echo -e "${GREEN}✓ Success${NC}"
    else
        echo -e "${RED}✗ Failed (Status: $status)${NC}"
    fi
}

# Test 1: Health check
echo "[1] Testing /health endpoint..."
response=$(curl -s -w "\n%{http_code}" "$API_URL/health")
http_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | sed '$d')

echo "Response: $body"
check_response "$http_code" 200
echo ""

# Test 2: Get API info
echo "[2] Testing / endpoint (API info)..."
response=$(curl -s -w "\n%{http_code}" "$API_URL/")
http_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | sed '$d')

echo "Response: $body" | head -c 100
echo "..."
check_response "$http_code" 200
echo ""

# Test 3: Single prediction (legitimate transaction)
echo "[3] Testing /predict endpoint (legitimate transaction)..."
response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1000.0,
    "oldbalanceOrig": 5000.0,
    "newbalanceOrig": 4000.0,
    "oldbalanceDest": 100.0,
    "newbalanceDest": 1100.0,
    "type": "PAYMENT"
  }')

http_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | sed '$d')

echo "Response: $body"
check_response "$http_code" 200
echo ""

# Test 4: Single prediction (suspicious transaction)
echo "[4] Testing /predict endpoint (suspicious transaction)..."
response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 900000.0,
    "oldbalanceOrig": 1000000.0,
    "newbalanceOrig": 100000.0,
    "oldbalanceDest": 0.0,
    "newbalanceDest": 900000.0,
    "type": "TRANSFER"
  }')

http_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | sed '$d')

echo "Response: $body"
check_response "$http_code" 200
echo ""

# Test 5: Batch prediction
echo "[5] Testing /predict_batch endpoint..."
response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/predict_batch" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {
        "amount": 500.0,
        "oldbalanceOrig": 2000.0,
        "newbalanceOrig": 1500.0,
        "oldbalanceDest": 500.0,
        "newbalanceDest": 1000.0,
        "type": "TRANSFER"
      },
      {
        "amount": 100000.0,
        "oldbalanceOrig": 150000.0,
        "newbalanceOrig": 50000.0,
        "oldbalanceDest": 1000.0,
        "newbalanceDest": 101000.0,
        "type": "CASH_IN"
      },
      {
        "amount": 5000.0,
        "oldbalanceOrig": 10000.0,
        "newbalanceOrig": 5000.0,
        "oldbalanceDest": 0.0,
        "newbalanceDest": 0.0,
        "type": "CASH_OUT"
      }
    ]
  }')

http_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | sed '$d')

echo "Response: $body" | python3 -m json.tool 2>/dev/null || echo "$body"
check_response "$http_code" 200
echo ""

# Test 6: Invalid request (missing field)
echo "[6] Testing error handling (missing field)..."
response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1000.0,
    "oldbalanceOrig": 5000.0
  }')

http_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | sed '$d')

echo "Response: $body"
check_response "$http_code" 400
echo ""

# Test 7: Invalid transaction type
echo "[7] Testing error handling (invalid type)..."
response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1000.0,
    "oldbalanceOrig": 5000.0,
    "newbalanceOrig": 4000.0,
    "oldbalanceDest": 100.0,
    "newbalanceDest": 1100.0,
    "type": "INVALID_TYPE"
  }')

http_code=$(echo "$response" | tail -n 1)
body=$(echo "$response" | sed '$d')

echo "Response: $body"
check_response "$http_code" 400
echo ""

echo "================================"
echo "Test complete!"
echo "================================"
