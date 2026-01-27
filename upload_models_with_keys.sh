#!/bin/bash
# Upload models with S3 keys pre-configured

cd /Volumes/Misha/ComfyUI
source venv/bin/activate

export AWS_ACCESS_KEY_ID='user_38YRmgsKQyYuMjfpbKCPeJsxB3m'
export AWS_SECRET_ACCESS_KEY='rps_Z067EF5RSR1SUGBIAB8G3AT0KIFDN9M6YP5ZIV2Hni2z1h'
export AWS_DEFAULT_REGION='us-ca-2'

echo "🚀 Starting model upload..."
echo "   This will take 20-40 minutes for ~20 GB of models"
echo "   Progress will be shown below"
echo ""

python3 upload_models_python.py
