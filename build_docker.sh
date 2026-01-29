#!/bin/bash
# Build and push Docker image for ComfyUI WAN 2.2 workflow

set -e

# Configuration
IMAGE_NAME="${1:-comfyui-wan22-irakim}"
IMAGE_TAG="${2:-latest}"
DOCKER_USERNAME="${DOCKER_USERNAME:-lutsco}"

FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "🚀 Building Docker image: ${FULL_IMAGE_NAME}"
echo ""

# Build image
echo "📦 Building image..."
docker build -t "${FULL_IMAGE_NAME}" .

echo ""
echo "✅ Build complete!"
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Test locally (optional):"
echo "   docker run -p 8188:8188 ${FULL_IMAGE_NAME}"
echo ""
echo "2. Login to Docker Hub:"
echo "   docker login"
echo ""
echo "3. Push to Docker Hub:"
echo "   docker push ${FULL_IMAGE_NAME}"
echo ""
echo "4. Deploy on RunPod:"
echo "   - Go to RunPod → Serverless → New Endpoint"
echo "   - Container Image: ${FULL_IMAGE_NAME}"
echo "   - GPU: RTX 3090/4090 or A100"
echo "   - Network Volume: Mount at /workspace/models"
echo "   - Handler Path: /workspace/handler.py"
echo ""
echo "💡 Usage:"
echo "   ./build_docker.sh [image-name] [tag]"
echo "   Example: ./build_docker.sh comfyui-wan22 v1.0"
