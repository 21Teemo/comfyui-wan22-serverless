# Testing Your RunPod Serverless Endpoint

## Quick Test Steps

### 1. Get Your Endpoint ID and API Key

**Endpoint ID:**
- Go to RunPod Dashboard → Serverless
- Click on your endpoint (`applicable_coffee_silkworm`)
- Copy the Endpoint ID (looks like: `abc123xyz`)

**API Key:**
- RunPod Dashboard → Settings → API Keys
- Create a new key or copy existing one
- Keep it secret!

### 2. Update Test Script

Edit `test_serverless.py`:
```python
ENDPOINT_ID = "your-actual-endpoint-id"
API_KEY = "your-actual-api-key"
```

### 3. Run Test

```bash
python3 test_serverless.py
```

## Manual Testing with cURL

### Submit Job

```bash
curl -X POST \
  "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "positive_prompt": "iraKim, 1girl, looking at camera",
      "negative_prompt": "blurry, distorted",
      "seed": 12345,
      "steps": 30,
      "cfg": 6.0,
      "width": 832,
      "height": 480,
      "length": 33
    }
  }'
```

Response:
```json
{
  "id": "job-abc123",
  "status": "IN_QUEUE"
}
```

### Check Status

```bash
curl -X GET \
  "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/status/job-abc123" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Stream Results (Alternative)

```bash
curl -X GET \
  "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/stream/job-abc123" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Python Example

```python
import requests
import time

ENDPOINT_ID = "your-endpoint-id"
API_KEY = "your-api-key"
API_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}"

# Submit job
response = requests.post(
    f"{API_URL}/run",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "input": {
            "positive_prompt": "iraKim, 1girl, looking at camera",
            "negative_prompt": "blurry, distorted",
            "seed": 12345,
            "steps": 30
        }
    }
)

job_id = response.json()["id"]
print(f"Job ID: {job_id}")

# Poll for completion
while True:
    status = requests.get(
        f"{API_URL}/status/{job_id}",
        headers={"Authorization": f"Bearer {API_KEY}"}
    ).json()
    
    if status["status"] == "COMPLETED":
        print("✅ Done!")
        print(status["output"])
        break
    elif status["status"] == "FAILED":
        print(f"❌ Failed: {status.get('error')}")
        break
    
    print(f"Status: {status['status']}...")
    time.sleep(5)
```

## Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `positive_prompt` | string | required | Main text prompt |
| `negative_prompt` | string | optional | Negative prompt |
| `seed` | int | random | Random seed |
| `steps` | int | 30 | Sampling steps |
| `cfg` | float | 6.0 | CFG scale |
| `width` | int | 832 | Video width |
| `height` | int | 480 | Video height |
| `length` | int | 33 | Number of frames |

## Expected Response Format

**Success:**
```json
{
  "status": "COMPLETED",
  "output": {
    "status": "completed",
    "prompt_id": "...",
    "videos": [
      {
        "filename": "ComfyUI_00001.mp4",
        "data": "hex_encoded_video_data",
        "size": 1234567
      }
    ],
    "images": []
  }
}
```

**Error:**
```json
{
  "status": "FAILED",
  "error": "Error message here"
}
```

## Troubleshooting

**"Endpoint not found"**
- Check ENDPOINT_ID is correct
- Verify endpoint is deployed and active

**"Unauthorized"**
- Check API_KEY is correct
- Verify API key has proper permissions

**"Job failed"**
- Check RunPod endpoint logs
- Verify models are on network volume
- Check handler logs for errors

**"Timeout"**
- Video generation takes 2-5 minutes
- Increase timeout in your code
- Check GPU is available

**"Models not found"**
- Verify network volume is mounted at `/workspace/models`
- Check model filenames match exactly
- Verify models are uploaded to volume

## Viewing Logs

1. RunPod Dashboard → Serverless → Your Endpoint
2. Click "Logs" tab
3. Check for:
   - ComfyUI startup messages
   - Model loading errors
   - Handler execution logs

## Quick Health Check

```bash
# Test if endpoint is accessible
curl -X GET \
  "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/health" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

(Note: Health endpoint may not exist - that's okay, test with actual job instead)
