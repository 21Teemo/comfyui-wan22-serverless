# Docker Image for WAN 2.2 Text-to-Video Workflow

This Docker image contains ComfyUI configured to run the `iraKim_text_to_video_wan` workflow on RunPod serverless.

## Quick Start

### 1. Build Image

```bash
./build_docker.sh comfyui-wan22-irakim latest
```

Or manually:
```bash
docker build -t lutsco/comfyui-wan22-irakim:latest .
```

### 2. Test Locally (Optional)

```bash
docker run -p 8188:8188 \
  -v /path/to/models:/workspace/models \
  lutsco/comfyui-wan22-irakim:latest
```

Then access ComfyUI at `http://localhost:8188`

### 3. Push to Docker Hub

```bash
docker login
docker push lutsco/comfyui-wan22-irakim:latest
```

### 4. Deploy on RunPod

1. **Create Network Volume:**
   - RunPod Dashboard → Network Volumes → Create
   - Size: 50-100GB
   - Upload your models:
     - `models/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors`
     - `models/vae/wan_2.1_vae.safetensors`
     - `models/diffusion_models/wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors`
     - `models/lora/iraKim-flux-high-noise.safetensors`

2. **Create Serverless Endpoint:**
   - Container Image: `lutsco/comfyui-wan22-irakim:latest`
   - GPU: RTX 3090 (24GB) or RTX 4090 (24GB) or A100 (40GB+)
   - Network Volume: Attach your volume
   - Volume Path: `/workspace/models`
   - Handler Path: `/workspace/handler.py`

3. **Get API Endpoint:**
   - Copy endpoint URL from RunPod dashboard
   - Get API key from Settings → API Keys

## API Usage

### Example Request

```python
import requests
import json

ENDPOINT_ID = "your-endpoint-id"
API_KEY = "your-api-key"
RUNPOD_API = f"https://api.runpod.ai/v2/{ENDPOINT_ID}"

# Submit job
response = requests.post(
    f"{RUNPOD_API}/run",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "input": {
            "positive_prompt": "iraKim, 1girl, looking at camera, serious expression",
            "negative_prompt": "blurry, distorted, bad quality",
            "seed": 12345,
            "steps": 30,
            "cfg": 6.0,
            "width": 832,
            "height": 480,
            "length": 33  # frames
        }
    }
)

job_id = response.json()["id"]
print(f"Job ID: {job_id}")

# Poll for status
import time
while True:
    status = requests.get(
        f"{RUNPOD_API}/status/{job_id}",
        headers={"Authorization": f"Bearer {API_KEY}"}
    ).json()
    
    if status["status"] == "COMPLETED":
        output = status.get("output", {})
        print("✅ Generation complete!")
        print(f"Videos: {len(output.get('videos', []))}")
        print(f"Images: {len(output.get('images', []))}")
        break
    elif status["status"] == "FAILED":
        print(f"❌ Failed: {status.get('error')}")
        break
    
    time.sleep(5)
```

### Input Parameters

- `positive_prompt` (string): Main text prompt
- `negative_prompt` (string, optional): Negative prompt
- `seed` (int, optional): Random seed (default: random)
- `steps` (int, optional): Sampling steps (default: 30)
- `cfg` (float, optional): CFG scale (default: 6.0)
- `width` (int, optional): Video width (default: 832)
- `height` (int, optional): Video height (default: 480)
- `length` (int, optional): Number of frames (default: 33)

### Output Format

```json
{
  "status": "completed",
  "prompt_id": "...",
  "videos": [
    {
      "filename": "ComfyUI_00001.mp4",
      "data": "hex_encoded_video_data",
      "size": 1234567
    }
  ],
  "images": [...],
  "outputs": {...}
}
```

## Model Requirements

The following models must be in your network volume:

```
/workspace/models/
├── text_encoders/
│   └── umt5_xxl_fp8_e4m3fn_scaled.safetensors (6.3 GB)
├── vae/
│   └── wan_2.1_vae.safetensors (242 MB)
├── diffusion_models/
│   └── wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors (13.3 GB)
└── lora/
    └── iraKim-flux-high-noise.safetensors (293 MB)
```

**Total: ~20 GB**

## Cost Estimation

**Per generation (2 minutes average):**
- Compute: 120s × $0.00031/s = **$0.037**
- Storage: $0.10/GB/month (for 20GB = $2/month)

**10 videos/week:**
- Compute: 10 × $0.037 = **$0.37/week** = **$1.60/month**
- Storage: **$2/month**
- **Total: ~$3.60/month**

## Troubleshooting

**Cold start slow?**
- First request: 30-60s (container + model loading)
- Subsequent: 2-5s (warm container)

**Out of memory?**
- Use A100 40GB or 80GB instead of RTX 3090/4090
- WAN 2.2 14B model needs ~20GB VRAM

**Models not found?**
- Verify network volume is mounted at `/workspace/models`
- Check model filenames match exactly
- Check ComfyUI logs in RunPod dashboard

**Handler errors?**
- Check logs: RunPod → Endpoint → Logs
- Verify workflow file exists at correct path
- Test locally first with `docker run`

## Files

- `Dockerfile`: Image definition
- `handler.py`: RunPod serverless handler
- `.dockerignore`: Files to exclude from build
- `build_docker.sh`: Build script
- `user/default/workflows/iraKim_text_to_video_wan .json`: Workflow file

## Development

**Modify workflow:**
1. Edit `user/default/workflows/iraKim_text_to_video_wan .json`
2. Rebuild: `./build_docker.sh`
3. Push: `docker push lutsco/comfyui-wan22-irakim:latest`
4. Update RunPod endpoint (or it auto-updates)

**Modify handler:**
1. Edit `handler.py`
2. Rebuild and push
3. Restart endpoint

## Notes

- Models are NOT included in image (use network volumes)
- Workflow is baked into image for faster startup
- Handler converts workflow JSON to API format automatically
- Video output is hex-encoded in JSON response (decode client-side)
