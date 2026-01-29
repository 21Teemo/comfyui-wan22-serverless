# Upload Models to RunPod Network Volume

Your network volume: **ira_kim_volume** (ID: `i36wtr1okx`)

## ⚠️ Important: S3 API Keys Required

RunPod requires **separate S3 API keys** (not your regular API key) to access network volumes via S3.

**Get S3 credentials:**
1. Go to: https://www.runpod.io/console/storage
2. Click on your network volume: **ira_kim_volume**
3. Look for "S3 API Access" or "Access Keys" section
4. Generate/View S3 Access Key and Secret Key

**If you don't have S3 keys**, use **Option 3** (temporary pod method) instead.

## Quick Start

### Option 1: Using Python Script (Requires S3 Keys)

**Prerequisites:**
```bash
pip install boto3
```

**Set your RunPod S3 keys (NOT the regular API key):**
```bash
export AWS_ACCESS_KEY_ID='your-s3-access-key'
export AWS_SECRET_ACCESS_KEY='your-s3-secret-key'
export AWS_DEFAULT_REGION='us-ca-2'
```

**Run the script:**
```bash
cd /Volumes/Misha/ComfyUI
python3 upload_models_python.py
```

### Option 2: Using AWS CLI

**Install AWS CLI:**
```bash
brew install awscli  # macOS
```

**Configure credentials:**
```bash
aws configure
# Access Key ID: (from RunPod Storage S3 API or use $RUNPOD_API_KEY)
# Secret Access Key: (same as API key or leave empty)
# Default region: us-ca-2
# Default output: json
```

**Or set environment variables:**
```bash
export AWS_ACCESS_KEY_ID='$RUNPOD_API_KEY'
export AWS_SECRET_ACCESS_KEY='$RUNPOD_API_KEY'
export AWS_DEFAULT_REGION='us-ca-2'
```

**Run the script:**
```bash
cd /Volumes/Misha/ComfyUI
./upload_models_to_volume.sh
```

## Models to Upload

The scripts will upload:

1. **Text Encoder** (6.3 GB)
   - `text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors`
   - Or: `text_encoders/umt5_xxl_fp16.safetensors`

2. **VAE** (242 MB)
   - `vae/wan_2.1_vae.safetensors`

3. **Diffusion Model** (13.3 GB) ⚠️ *Largest file - takes 15-30 minutes*
   - `diffusion_models/wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors`

4. **LoRA** (293 MB)
   - `loras/iraKim-flux-high-noise.safetensors`

**Total size:** ~20 GB

## Verify Upload

After uploading, verify files are on the volume:

```bash
aws s3 ls s3://i36wtr1okx/ --endpoint-url https://s3api-us-ca-2.runpod.io --recursive
```

Or using Python:
```python
import boto3
s3 = boto3.client('s3', endpoint_url='https://s3api-us-ca-2.runpod.io', region_name='us-ca-2')
s3.list_objects_v2(Bucket='i36wtr1okx', Prefix='text_encoders/')
```

### Option 3: Using Temporary Pod (No S3 Keys Needed) ⭐ Recommended if S3 fails

**This method works without S3 API keys:**

```bash
cd /Volumes/Misha/ComfyUI
./upload_via_pod.sh
```

The script will:
1. Ask for your pod's SSH details
2. Create directories on the network volume
3. Upload all models via SCP

**Or manually:**
1. Create a temporary RunPod Pod (any GPU, smallest is fine)
2. Attach network volume: **ira_kim_volume**
3. SSH into the pod
4. Run the upload script or use SCP commands

## Manual Upload (Alternative)

If scripts don't work, you can upload manually:

1. **Create a temporary RunPod Pod** with the network volume attached
2. **SSH into the pod**
3. **Use SCP to upload:**
   ```bash
   scp -P <port> /Volumes/Misha/ComfyUI/models/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors root@<pod-ip>:/workspace/models/text_encoders/
   ```

## Troubleshooting

**Error: "Access Denied"**
- Check your RunPod API key is correct
- Ensure the API key has access to network volumes

**Error: "Bucket not found"**
- Verify volume ID: `i36wtr1okx`
- Check volume is in data center: `US-CA-2`

**Upload is slow**
- Large files (13+ GB) take time
- Use `--no-progress` flag to reduce output overhead
- Consider using a pod with faster network connection

**Files not appearing**
- Wait a few seconds for S3 eventual consistency
- Check with `aws s3 ls` command
- Verify you're using the correct endpoint URL

## After Upload

Once models are uploaded:

1. **Redeploy your serverless endpoint** (or it will auto-detect on next run)
2. **Check handler logs** - it will show which models it finds:
   ```
   Network volume models found at: /workspace/models
   text_encoders: 1 model files
   vae: 1 model files
   diffusion_models: 1 model files
   loras: 1 model files
   ```

3. **Test the endpoint** - models should now be found!
