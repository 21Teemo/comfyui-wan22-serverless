#!/bin/bash
# Start ComfyUI from Misha drive with auto-restart

cd /Volumes/Misha/ComfyUI

# Kill any existing ComfyUI processes
pkill -f "python.*main.py" 2>/dev/null
sleep 2

# Start ComfyUI with nohup to keep it running even if terminal closes
# Memory optimization flags available:
# --lowvram: Split UNet to use less VRAM
# --novram: When lowvram isn't enough
# --cpu-vae: Run VAE on CPU to save VRAM
# --reserve-vram 2.0: Reserve VRAM for OS
# Remove --cpu if you have a GPU and want better performance
nohup /usr/local/opt/python@3.11/bin/python3.11 main.py --listen 127.0.0.1 --port 8188 --cpu > /tmp/comfyui_misha.log 2>&1 &

COMFY_PID=$!
echo "ComfyUI starting (PID: $COMFY_PID)..."
echo "Logs: /tmp/comfyui_misha.log"
echo ""
echo "Waiting for server to start..."
sleep 20

if curl -s http://127.0.0.1:8188 > /dev/null 2>&1; then
    echo ""
    echo "✓✓✓ ComfyUI is running!"
    echo ""
    echo "Open: http://127.0.0.1:8188"
    echo "Process ID: $COMFY_PID"
    echo ""
    echo "To stop: kill $COMFY_PID"
    echo "To view logs: tail -f /tmp/comfyui_misha.log"
else
    echo "Server may still be initializing..."
    echo "Check logs: tail -f /tmp/comfyui_misha.log"
fi
