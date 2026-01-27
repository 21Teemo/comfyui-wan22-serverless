#!/bin/bash
# Upload models using AWS CLI (works around Python SSL issues)
# Forces single-part uploads to avoid RunPod multipart issues

set -e

export AWS_ACCESS_KEY_ID='user_38YRmgsKQyYuMjfpbKCPeJsxB3m'
export AWS_SECRET_ACCESS_KEY='rps_Z067EF5RSR1SUGBIAB8G3AT0KIFDN9M6YP5ZIV2Hni2z1h'
export AWS_DEFAULT_REGION='us-ca-2'

BUCKET="i36wtr1okx"
ENDPOINT="https://s3api-us-ca-2.runpod.io"
LOCAL_BASE="/Volumes/Misha/ComfyUI/models"

echo "🚀 Uploading models using AWS CLI (single-part uploads)"
echo "   Bucket: $BUCKET"
echo "   Endpoint: $ENDPOINT"
echo ""

# Configure AWS CLI to use single-part uploads
# Create config file to disable multipart uploads
mkdir -p ~/.aws
cat > ~/.aws/config <<EOF
[default]
s3 =
    multipart_threshold = 100GB
    multipart_chunksize = 100GB
EOF
echo "✅ Configured AWS CLI for single-part uploads"
echo ""

# Upload models (smallest first)
echo "1️⃣  VAE (242 MB)..."
aws s3 cp "${LOCAL_BASE}/vae/wan_2.1_vae.safetensors" \
  "s3://${BUCKET}/vae/wan_2.1_vae.safetensors" \
  --endpoint-url "$ENDPOINT" \
  --region us-ca-2 \
  --no-progress
echo "   ✅ VAE uploaded"
echo ""

echo "2️⃣  LoRA (293 MB)..."
aws s3 cp "${LOCAL_BASE}/loras/iraKim-flux-high-noise.safetensors" \
  "s3://${BUCKET}/loras/iraKim-flux-high-noise.safetensors" \
  --endpoint-url "$ENDPOINT" \
  --region us-ca-2 \
  --no-progress
echo "   ✅ LoRA uploaded"
echo ""

echo "3️⃣  Text Encoder (6.3 GB) - this will take 5-10 minutes..."
TEXT_ENCODER="${LOCAL_BASE}/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors"
if [ -f "$TEXT_ENCODER" ]; then
  aws s3 cp "$TEXT_ENCODER" \
    "s3://${BUCKET}/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors" \
    --endpoint-url "$ENDPOINT" \
    --region us-ca-2 \
    --no-progress
else
  TEXT_ENCODER_ALT="${LOCAL_BASE}/text_encoders/umt5_xxl_fp16.safetensors"
  if [ -f "$TEXT_ENCODER_ALT" ]; then
    aws s3 cp "$TEXT_ENCODER_ALT" \
      "s3://${BUCKET}/text_encoders/umt5_xxl_fp16.safetensors" \
      --endpoint-url "$ENDPOINT" \
      --region us-ca-2 \
      --no-progress
  fi
fi
echo "   ✅ Text Encoder uploaded"
echo ""

echo "4️⃣  Diffusion Model (13.3 GB) - this will take 15-30 minutes..."
aws s3 cp "${LOCAL_BASE}/diffusion_models/wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors" \
  "s3://${BUCKET}/diffusion_models/wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors" \
  --endpoint-url "$ENDPOINT" \
  --region us-ca-2 \
  --no-progress
echo "   ✅ Diffusion Model uploaded"
echo ""

echo "✅ All models uploaded successfully!"
echo ""
echo "📝 Verify upload:"
echo "   aws s3 ls s3://${BUCKET}/ --endpoint-url ${ENDPOINT} --recursive"
