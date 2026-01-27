#!/usr/bin/env python3
"""
Test RunPod Serverless Endpoint (Synchronous)
Endpoint: https://api.runpod.ai/v2/11bu8yupz6eou9/runsync
"""
import os
import requests
import json
import time

ENDPOINT_ID = "11bu8yupz6eou9"
API_KEY = os.getenv("RUNPOD_API_KEY")

if not API_KEY:
    print("⚠️  Please set RUNPOD_API_KEY environment variable:")
    print("   export RUNPOD_API_KEY='rpa_...'")
    exit(1)

ENDPOINT_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/runsync"

print("🚀 Testing RunPod Serverless Endpoint (Synchronous)")
print(f"   Endpoint: {ENDPOINT_URL}")
print()

# Simple request using default workflow
payload = {
    "input": {
        "prompt": "iraKim, 1girl, looking at camera, serious expression, professional setting, soft lighting"
    }
}

print("📤 Sending request...")
print(f"   Prompt: {payload['input']['prompt']}")
print()

try:
    response = requests.post(
        ENDPOINT_URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=600  # 10 minutes timeout
    )
    
    response.raise_for_status()
    result = response.json()
    
    print("✅ Response received:")
    print(f"   Status: {result.get('status', 'UNKNOWN')}")
    print(f"   ID: {result.get('id', 'N/A')}")
    
    if result.get('status') == 'COMPLETED':
        output = result.get('output', {})
        images = output.get('images', [])
        
        print(f"\n📹 Generated {len(images)} output(s):")
        for i, img in enumerate(images, 1):
            filename = img.get('filename', 'unknown')
            img_type = img.get('type', 'unknown')
            data_len = len(img.get('data', ''))
            print(f"   {i}. {filename} ({img_type}, {data_len} chars)")
        
        # Save first video/image if base64
        if images and images[0].get('type') == 'base64':
            import base64
            filename = images[0].get('filename', 'output.mp4')
            data = images[0].get('data', '')
            
            # Determine extension
            if filename.endswith('.mp4') or filename.endswith('.webm'):
                output_file = f"output_{int(time.time())}.mp4"
            else:
                output_file = f"output_{int(time.time())}.png"
            
            with open(output_file, 'wb') as f:
                f.write(base64.b64decode(data))
            
            print(f"\n💾 Saved to: {output_file}")
    
    elif result.get('status') == 'FAILED':
        print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
    
    else:
        print(f"\n⏳ Status: {result.get('status')}")
        print(json.dumps(result, indent=2))

except requests.exceptions.Timeout:
    print("❌ Request timed out (exceeded 10 minutes)")
except requests.exceptions.HTTPError as e:
    print(f"❌ HTTP Error: {e}")
    if hasattr(e.response, 'text'):
        print(f"   Response: {e.response.text[:500]}")
except Exception as e:
    print(f"❌ Error: {e}")
