# ComfyUI WAN 2.2 Text-to-Video Serverless

RunPod serverless endpoint for WAN 2.2 text-to-video generation with iraKim workflow.

## Repository Structure

```
.
├── Dockerfile              # Docker image definition
├── handler.py              # RunPod serverless handler
├── user/
│   └── default/
│       └── workflows/
│           └── iraKim_text_to_video_wan .json  # Workflow file
└── README.md
```

## Deployment

### RunPod GitHub Integration

1. **Connect GitHub to RunPod:**
   - RunPod Dashboard → Serverless → New Endpoint
   - Select "Import GitHub Repository"
   - Authorize RunPod to access your GitHub
   - Select this repository

2. **Configure Endpoint:**
   - **Handler Path:** `/workspace/handler.py`
   - **GPU:** RTX 3090/4090 (24GB) or A100 (40GB+)
   - **Container Disk:** 30GB minimum
   - **Network Volume:** Mount at `/workspace/models`

3. **Network Volume Setup:**
   - Create volume (50-100GB)
   - Upload models:
     - `models/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors`
     - `models/vae/wan_2.1_vae.safetensors`
     - `models/diffusion_models/wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors`
     - `models/lora/iraKim-flux-high-noise.safetensors`

## API Usage

```python
import requests

ENDPOINT_ID = "your-endpoint-id"
API_KEY = "your-api-key"
API_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}"

response = requests.post(
    f"{API_URL}/run",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={
        "input": {
            "positive_prompt": "iraKim, 1girl, looking at camera",
            "negative_prompt": "blurry, distorted, bad quality",
            "seed": 12345,
            "steps": 30,
            "cfg": 6.0,
            "width": 832,
            "height": 480,
            "length": 33
        }
    }
)

job_id = response.json()["id"]
```

## Input Parameters

- `positive_prompt` (string, required): Main text prompt
- `negative_prompt` (string, optional): Negative prompt
- `seed` (int, optional): Random seed
- `steps` (int, optional): Sampling steps (default: 30)
- `cfg` (float, optional): CFG scale (default: 6.0)
- `width` (int, optional): Video width (default: 832)
- `height` (int, optional): Video height (default: 480)
- `length` (int, optional): Number of frames (default: 33)

## Local Development

```bash
# Build locally
docker build -t comfyui-wan22:latest .

# Test locally
docker run -p 8188:8188 \
  -v /path/to/models:/workspace/models \
  comfyui-wan22:latest
```

## Updating

1. Make changes to `handler.py` or `Dockerfile`
2. Commit and push to GitHub
3. RunPod will rebuild automatically (or trigger manually)

## Requirements

- PyTorch 2.2.0+ (for comfy-kitchen)
- CUDA 11.8+
- Python 3.10

## License

See ComfyUI license for base components.
