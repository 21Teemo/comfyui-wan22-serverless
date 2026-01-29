#!/usr/bin/env python3
"""
Upload models to RunPod Network Volume via S3 API
Network Volume: ira_kim_volume (i36wtr1okx)
Data Center: US-CA-2
"""

import os
import sys
import boto3
from pathlib import Path
from botocore.exceptions import ClientError, NoCredentialsError

# RunPod S3 Configuration
BUCKET_NAME = "i36wtr1okx"
ENDPOINT_URL = "https://s3api-us-ca-2.runpod.io"
REGION = "us-ca-2"

# Local paths
LOCAL_BASE = Path("/Volumes/Misha/ComfyUI/models")

# Models to upload - ORDERED BY SIZE (smallest first for faster testing)
MODELS = [
    {
        "local": LOCAL_BASE / "vae" / "wan_2.1_vae.safetensors",
        "remote": "vae/wan_2.1_vae.safetensors",
        "alt": None,
        "alt_remote": None,
        "name": "VAE",
        "size_gb": 0.242
    },
    {
        "local": LOCAL_BASE / "loras" / "iraKim-flux-high-noise.safetensors",
        "remote": "loras/iraKim-flux-high-noise.safetensors",
        "alt": None,
        "alt_remote": None,
        "name": "LoRA",
        "size_gb": 0.293
    },
    {
        "local": LOCAL_BASE / "text_encoders" / "umt5_xxl_fp8_e4m3fn_scaled.safetensors",
        "remote": "text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors",
        "alt": LOCAL_BASE / "text_encoders" / "umt5_xxl_fp16.safetensors",
        "alt_remote": "text_encoders/umt5_xxl_fp16.safetensors",
        "name": "Text Encoder",
        "size_gb": 6.3
    },
    {
        "local": LOCAL_BASE / "diffusion_models" / "wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors",
        "remote": "diffusion_models/wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors",
        "alt": None,
        "alt_remote": None,
        "name": "Diffusion Model",
        "size_gb": 13.3
    }
]


def format_size(size_bytes):
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def upload_file(s3_client, local_path, remote_key, model_name):
    """Upload a file to S3 with progress"""
    if not local_path.exists():
        print(f"   ⚠️  {model_name} not found at {local_path}")
        return False
    
    file_size = local_path.stat().st_size
    print(f"   📤 Uploading {model_name} ({format_size(file_size)})...")
    
    try:
        # Disable multipart uploads - RunPod S3 seems to have issues with multipart
        # Use single-part upload for all files (slower but more reliable)
        from boto3.s3.transfer import TransferConfig
        
        # Set multipart_threshold very high to force single-part uploads
        config = TransferConfig(
            multipart_threshold=1024 * 1024 * 1024 * 100,  # 100 GB - effectively disables multipart
            use_threads=False
        )
        
        print(f"   ⚙️  Using single-part upload (no multipart)...")
        s3_client.upload_file(
            str(local_path),
            BUCKET_NAME,
            remote_key,
            Config=config
        )
        print(f"   ✅ {model_name} uploaded successfully")
        return True
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', '')
        error_msg = str(e)
        print(f"   ❌ Error uploading {model_name}: {error_code}")
        print(f"      {error_msg}")
        
        # Try single-part upload for smaller files or as fallback
        if file_size < 100 * 1024 * 1024:  # < 100 MB
            print(f"   🔄 Retrying with single-part upload...")
            try:
                config = TransferConfig(use_threads=False)
                s3_client.upload_file(
                    str(local_path),
                    BUCKET_NAME,
                    remote_key,
                    Config=config
                )
                print(f"   ✅ {model_name} uploaded successfully (single-part)")
                return True
            except Exception as e2:
                print(f"   ❌ Retry also failed: {e2}")
        
        return False


def main():
    print("🚀 Uploading models to RunPod Network Volume")
    print(f"   Volume: {BUCKET_NAME}")
    print(f"   Endpoint: {ENDPOINT_URL}")
    print()
    
    # Check for credentials - try multiple sources
    access_key = (os.environ.get("AWS_ACCESS_KEY_ID") or 
                  os.environ.get("RUNPOD_S3_ACCESS_KEY") or
                  os.environ.get("RUNPOD_API_KEY"))
    secret_key = (os.environ.get("AWS_SECRET_ACCESS_KEY") or 
                 os.environ.get("RUNPOD_S3_SECRET_KEY") or
                 os.environ.get("RUNPOD_API_KEY"))
    
    if not access_key:
        print("❌ S3 credentials not found!")
        print()
        print("Try one of these methods:")
        print()
        print("Method 1: Use RunPod API key (may work for S3):")
        print("  export RUNPOD_API_KEY='your-runpod-api-key'")
        print("  export AWS_DEFAULT_REGION='us-ca-2'")
        print()
        print("Method 2: Get S3-specific keys from RunPod:")
        print("  1. Go to: https://www.runpod.io/console/storage")
        print("  2. Click on your network volume: ira_kim_volume")
        print("  3. Look for 'S3 API Access' or 'Access Keys' section")
        print("  4. Generate/View S3 Access Key and Secret Key")
        print("  export AWS_ACCESS_KEY_ID='your-s3-access-key'")
        print("  export AWS_SECRET_ACCESS_KEY='your-s3-secret-key'")
        print()
        print("Method 3: Use temporary pod (no keys needed):")
        print("  ./upload_via_pod.sh")
        print()
        sys.exit(1)
    
    # Create S3 client
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=ENDPOINT_URL,
            region_name=REGION,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        
        # Test connection
        print("🔌 Testing connection...")
        s3_client.head_bucket(Bucket=BUCKET_NAME)
        print("   ✅ Connected to network volume")
        print()
    except NoCredentialsError:
        print("❌ AWS credentials not configured")
        sys.exit(1)
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', '')
        if error_code == '404':
            print(f"❌ Bucket {BUCKET_NAME} not found. Check volume ID.")
        elif error_code == '403' or 'Forbidden' in str(e):
            print(f"❌ Access Forbidden (403)")
            print()
            print("This usually means:")
            print("  1. S3 credentials are incorrect or missing")
            print("  2. You're using the regular API key instead of S3 keys")
            print("  3. S3 access hasn't been enabled for your account")
            print()
            print("Solutions:")
            print("  • Get S3-specific keys from: https://www.runpod.io/console/storage")
            print("  • Or use alternative method: Create a temporary pod with volume mounted")
            print("  • See UPLOAD_MODELS_GUIDE.md for pod-based upload method")
        else:
            print(f"❌ Error connecting to S3: {e}")
            print(f"   Error code: {error_code}")
        sys.exit(1)
    
    # Clean up any existing directory placeholder objects that might conflict
    print("🧹 Cleaning up any directory placeholders...")
    try:
        for prefix in ["text_encoders/", "vae/", "diffusion_models/", "loras/"]:
            try:
                response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix, MaxKeys=1000)
                if 'Contents' in response:
                    for obj in response['Contents']:
                        # Delete directory placeholder objects (empty objects ending with /)
                        if obj['Key'].endswith('/') and obj['Size'] == 0:
                            s3_client.delete_object(Bucket=BUCKET_NAME, Key=obj['Key'])
                            print(f"   Removed placeholder: {obj['Key']}")
            except:
                pass
    except:
        pass
    print()
    
    # Upload models
    print("📦 Uploading models...")
    print()
    
    uploaded = 0
    for i, model in enumerate(MODELS, 1):
        print(f"{i}️⃣  {model['name']} ({model['size_gb']} GB)...")
        
        # Try primary path
        if model["local"].exists():
            if upload_file(s3_client, model["local"], model["remote"], model["name"]):
                uploaded += 1
        # Try alternative path
        elif model.get("alt") and model["alt"].exists():
            if upload_file(s3_client, model["alt"], model.get("alt_remote", model["remote"]), model["name"]):
                uploaded += 1
        else:
            print(f"   ⚠️  {model['name']} not found (skipping)")
        
        print()
    
    print("✅ Upload complete!")
    print(f"   Uploaded {uploaded}/{len(MODELS)} models")
    print()
    print("📝 Verify upload:")
    print(f"   aws s3 ls s3://{BUCKET_NAME}/ --endpoint-url {ENDPOINT_URL} --recursive")


if __name__ == "__main__":
    main()
