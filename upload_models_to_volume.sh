#!/bin/bash
# Upload models to RunPod Network Volume via S3 API
# Network Volume: ira_kim_volume (i36wtr1okx)
# Data Center: US-CA-2

set -e

# RunPod S3 Configuration
BUCKET_NAME="i36wtr1okx"
ENDPOINT_URL="https://s3api-us-ca-2.runpod.io"
REGION="us-ca-2"

# Local paths
LOCAL_BASE="/Volumes/Misha/ComfyUI/models"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Installing..."
    echo ""
    echo "Install AWS CLI:"
    echo "  macOS: brew install awscli"
    echo "  Or download from: https://aws.amazon.com/cli/"
    exit 1
fi

# Check if AWS credentials are configured
if ! aws configure get aws_access_key_id &> /dev/null; then
    echo "⚠️  AWS credentials not configured."
    echo ""
    echo "You need to configure AWS credentials for RunPod S3:"
    echo "  1. Get your RunPod API key: https://www.runpod.io/console/user/settings"
    echo "  2. Run: aws configure"
    echo "     - Access Key ID: Your RunPod API key"
    echo "     - Secret Access Key: (leave empty or use same as API key)"
    echo "     - Default region: us-ca-2"
    echo "     - Default output: json"
    echo ""
    echo "Or set environment variables:"
    echo "  export AWS_ACCESS_KEY_ID='your-runpod-api-key'"
    echo "  export AWS_SECRET_ACCESS_KEY='your-runpod-api-key'"
    echo "  export AWS_DEFAULT_REGION='us-ca-2'"
    exit 1
fi

echo "🚀 Uploading models to RunPod Network Volume..."
echo "   Volume: $BUCKET_NAME"
echo "   Endpoint: $ENDPOINT_URL"
echo ""

# Create directories on volume (if they don't exist)
echo "📁 Ensuring directories exist on volume..."
aws s3api put-object \
    --bucket "$BUCKET_NAME" \
    --key "text_encoders/" \
    --endpoint-url "$ENDPOINT_URL" \
    --region "$REGION" \
    --no-cli-pager || true

aws s3api put-object \
    --bucket "$BUCKET_NAME" \
    --key "vae/" \
    --endpoint-url "$ENDPOINT_URL" \
    --region "$REGION" \
    --no-cli-pager || true

aws s3api put-object \
    --bucket "$BUCKET_NAME" \
    --key "diffusion_models/" \
    --endpoint-url "$ENDPOINT_URL" \
    --region "$REGION" \
    --no-cli-pager || true

aws s3api put-object \
    --bucket "$BUCKET_NAME" \
    --key "loras/" \
    --endpoint-url "$ENDPOINT_URL" \
    --region "$REGION" \
    --no-cli-pager || true

echo ""

# Upload models
echo "📦 Uploading models..."
echo ""

# Text Encoder
TEXT_ENCODER="${LOCAL_BASE}/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors"
if [ -f "$TEXT_ENCODER" ]; then
    echo "1️⃣  Text Encoder (6.3 GB)..."
    aws s3 cp "$TEXT_ENCODER" \
        "s3://${BUCKET_NAME}/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors" \
        --endpoint-url "$ENDPOINT_URL" \
        --region "$REGION" \
        --no-progress
    echo "   ✅ Text encoder uploaded"
else
    # Try alternative filename
    TEXT_ENCODER_ALT="${LOCAL_BASE}/text_encoders/umt5_xxl_fp16.safetensors"
    if [ -f "$TEXT_ENCODER_ALT" ]; then
        echo "1️⃣  Text Encoder (umt5_xxl_fp16.safetensors)..."
        aws s3 cp "$TEXT_ENCODER_ALT" \
            "s3://${BUCKET_NAME}/text_encoders/umt5_xxl_fp16.safetensors" \
            --endpoint-url "$ENDPOINT_URL" \
            --region "$REGION" \
            --no-progress
        echo "   ✅ Text encoder uploaded"
    else
        echo "   ⚠️  Text encoder not found (skipping)"
    fi
fi

echo ""

# VAE
VAE="${LOCAL_BASE}/vae/wan_2.1_vae.safetensors"
if [ -f "$VAE" ]; then
    echo "2️⃣  VAE (242 MB)..."
    aws s3 cp "$VAE" \
        "s3://${BUCKET_NAME}/vae/wan_2.1_vae.safetensors" \
        --endpoint-url "$ENDPOINT_URL" \
        --region "$REGION" \
        --no-progress
    echo "   ✅ VAE uploaded"
else
    echo "   ⚠️  VAE not found (skipping)"
fi

echo ""

# Diffusion Model
DIFFUSION="${LOCAL_BASE}/diffusion_models/wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors"
if [ -f "$DIFFUSION" ]; then
    echo "3️⃣  Diffusion Model (13.3 GB) - this will take 15-30 minutes..."
    aws s3 cp "$DIFFUSION" \
        "s3://${BUCKET_NAME}/diffusion_models/wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors" \
        --endpoint-url "$ENDPOINT_URL" \
        --region "$REGION" \
        --no-progress
    echo "   ✅ Diffusion model uploaded"
else
    echo "   ⚠️  Diffusion model not found (skipping)"
fi

echo ""

# LoRA
LORA="${LOCAL_BASE}/loras/iraKim-flux-high-noise.safetensors"
if [ -f "$LORA" ]; then
    echo "4️⃣  LoRA (293 MB)..."
    aws s3 cp "$LORA" \
        "s3://${BUCKET_NAME}/loras/iraKim-flux-high-noise.safetensors" \
        --endpoint-url "$ENDPOINT_URL" \
        --region "$REGION" \
        --no-progress
    echo "   ✅ LoRA uploaded"
else
    echo "   ⚠️  LoRA not found (skipping)"
fi

echo ""
echo "✅ Upload complete!"
echo ""
echo "📝 Verify upload:"
echo "   aws s3 ls s3://${BUCKET_NAME}/ --endpoint-url ${ENDPOINT_URL} --recursive"
