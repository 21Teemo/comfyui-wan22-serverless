#!/bin/bash
# Test RunPod Serverless Endpoint
# Endpoint: https://api.runpod.ai/v2/11bu8yupz6eou9/run

ENDPOINT_ID="11bu8yupz6eou9"
API_KEY="${RUNPOD_API_KEY}"

if [ -z "$API_KEY" ]; then
    echo "⚠️  Please set RUNPOD_API_KEY environment variable:"
    echo "   export RUNPOD_API_KEY='rpa_...'"
    exit 1
fi

echo "🚀 Testing RunPod Serverless Endpoint"
echo "   Endpoint: https://api.runpod.ai/v2/${ENDPOINT_ID}/run"
echo ""

# Option 1: Use default workflow (simplest)
echo "📝 Option 1: Using default workflow (will use your iraKim workflow)"
curl -X POST \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "prompt": "iraKim, 1girl, looking at camera, serious expression, professional setting"
    }
  }' \
  "https://api.runpod.ai/v2/${ENDPOINT_ID}/run" | jq '.'

echo ""
echo "---"
echo ""

# Option 2: Async request (returns job ID immediately)
echo "📝 Option 2: Async request (returns job ID)"
JOB_RESPONSE=$(curl -s -X POST \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "prompt": "iraKim, 1girl, looking at camera, serious expression"
    }
  }' \
  "https://api.runpod.ai/v2/${ENDPOINT_ID}/run")

JOB_ID=$(echo "$JOB_RESPONSE" | jq -r '.id // .jobId // empty')

if [ -n "$JOB_ID" ] && [ "$JOB_ID" != "null" ]; then
    echo "✅ Job submitted: $JOB_ID"
    echo ""
    echo "📊 Check status:"
    echo "   curl -H \"Authorization: Bearer ${API_KEY}\" \\"
    echo "        https://api.runpod.ai/v2/${ENDPOINT_ID}/status/${JOB_ID}"
else
    echo "❌ Failed to get job ID"
    echo "$JOB_RESPONSE" | jq '.'
fi
