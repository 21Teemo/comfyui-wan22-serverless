#!/usr/bin/env bash
set -e
source /Volumes/Misha/ComfyUI/.venvs/comfyui/bin/activate
cd /Volumes/Misha/ComfyUI
python main.py --listen 0.0.0.0 --port 8188
