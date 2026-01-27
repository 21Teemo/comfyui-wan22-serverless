#!/bin/bash
# Quick test with your API key pre-configured

ENDPOINT_ID="11bu8yupz6eou9"
API_KEY="${RUNPOD_API_KEY:-your_api_key_here}"

if [ "$API_KEY" = "your_api_key_here" ]; then
    echo "⚠️  Please set RUNPOD_API_KEY environment variable:"
    echo "   export RUNPOD_API_KEY='rpa_...'"
    exit 1
fi

echo "🚀 Quick Test - RunPod Serverless Endpoint"
echo "   Endpoint: https://api.runpod.ai/v2/${ENDPOINT_ID}/runsync"
echo ""

# Simple synchronous request
curl -X POST \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "prompt": "iraKim, 1girl, looking at camera, serious expression, professional setting"
    }
  }' \
  "https://api.runpod.ai/v2/${ENDPOINT_ID}/runsync"
