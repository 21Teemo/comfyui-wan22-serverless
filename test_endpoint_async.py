#!/usr/bin/env python3
"""
Test RunPod Serverless Endpoint (Asynchronous)
Endpoint: https://api.runpod.ai/v2/11bu8yupz6eou9/run
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

ENDPOINT_RUN = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/run"
ENDPOINT_STATUS = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/status"

print("🚀 Testing RunPod Serverless Endpoint (Asynchronous)")
print(f"   Run: {ENDPOINT_RUN}")
print()

# Submit job
payload = {
    "input": {
        "prompt": "iraKim, 1girl, looking at camera, serious expression, professional setting"
    }
}

print("📤 Submitting job...")
try:
    response = requests.post(
        ENDPOINT_RUN,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=30
    )
    
    response.raise_for_status()
    result = response.json()
    
    # Get job ID (RunPod uses different field names)
    job_id = result.get('id') or result.get('jobId') or result.get('job_id')
    
    if not job_id:
        print("❌ Failed to get job ID")
        print(json.dumps(result, indent=2))
        exit(1)
    
    print(f"✅ Job submitted: {job_id}")
    print(f"\n📊 Polling for status...")
    print()
    
    # Poll for completion
    max_wait = 600  # 10 minutes
    waited = 0
    poll_interval = 5
    
    while waited < max_wait:
        status_response = requests.get(
            f"{ENDPOINT_STATUS}/{job_id}",
            headers={"Authorization": f"Bearer {API_KEY}"},
            timeout=10
        )
        
        status_response.raise_for_status()
        status_result = status_response.json()
        
        status = status_result.get('status', 'UNKNOWN')
        
        if status == 'COMPLETED':
            print("✅ Job completed!")
            output = status_result.get('output', {})
            images = output.get('images', [])
            
            print(f"\n📹 Generated {len(images)} output(s):")
            for i, img in enumerate(images, 1):
                filename = img.get('filename', 'unknown')
                img_type = img.get('type', 'unknown')
                print(f"   {i}. {filename} ({img_type})")
            
            # Save first output if base64
            if images and images[0].get('type') == 'base64':
                import base64
                filename = images[0].get('filename', 'output.mp4')
                data = images[0].get('data', '')
                
                output_file = f"output_{int(time.time())}.mp4" if filename.endswith('.mp4') else f"output_{int(time.time())}.png"
                
                with open(output_file, 'wb') as f:
                    f.write(base64.b64decode(data))
                
                print(f"\n💾 Saved to: {output_file}")
            
            break
            
        elif status == 'FAILED':
            print(f"❌ Job failed: {status_result.get('error', 'Unknown error')}")
            break
            
        else:
            print(f"⏳ Status: {status} ({waited}s/{max_wait}s)")
            time.sleep(poll_interval)
            waited += poll_interval
    
    if waited >= max_wait:
        print(f"⏱️  Timeout after {max_wait} seconds")

except requests.exceptions.HTTPError as e:
    print(f"❌ HTTP Error: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"   Response: {e.response.text[:500]}")
except Exception as e:
    print(f"❌ Error: {e}")
