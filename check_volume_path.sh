#!/bin/bash
# Check where network volume is mounted on RunPod serverless

echo "🔍 Checking network volume location..."
echo ""

# This would run inside the container - showing what to check
echo "To check volume location, SSH into a pod or check RunPod logs for:"
echo "   '📂 Checking /workspace contents:'"
echo ""
echo "Or manually check in RunPod console:"
echo "   1. Go to your endpoint"
echo "   2. Check logs for workspace contents"
echo "   3. Look for volume directory names"
echo ""
echo "Common volume mount paths:"
echo "   - /workspace/iraKim_volume/models"
echo "   - /workspace/ira_kim_volume/models"
echo "   - /workspace/models (if mounted directly)"
echo ""
echo "Once you find the path, update handler.py DEFAULT_WORKFLOW_FILE path if needed"
