#!/usr/bin/env python3
"""
Export ComfyUI workflow in API format
Run this locally with ComfyUI running to get the proper API format
"""
import json
import requests
import sys

COMFYUI_URL = "http://127.0.0.1:8188"
WORKFLOW_FILE = "user/default/workflows/iraKim_text_to_video_wan .json"

def load_workflow():
    """Load workflow from file"""
    with open(WORKFLOW_FILE, 'r') as f:
        return json.load(f)

def get_api_workflow(workflow_data):
    """Get API format from ComfyUI"""
    # ComfyUI has an endpoint to convert UI workflow to API format
    # But we can also use the workflow directly if it's already in API format
    
    # Try to get workflow API format via ComfyUI's API
    try:
        response = requests.post(
            f"{COMFYUI_URL}/prompt",
            json={"prompt": workflow_data},
            timeout=5
        )
        # This will validate and return errors if invalid
        if response.status_code == 200:
            print("✅ Workflow is valid!")
            return workflow_data
        else:
            print(f"❌ Workflow validation failed: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print("⚠️  ComfyUI not running. Cannot validate workflow.")
        print("   Start ComfyUI first: python main.py --listen 127.0.0.1 --port 8188")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("📄 Loading workflow...")
    workflow = load_workflow()
    
    print("🔄 Converting to API format...")
    api_workflow = get_api_workflow(workflow)
    
    if api_workflow:
        # Save API format
        output_file = "user/default/workflows/iraKim_text_to_video_wan_api.json"
        with open(output_file, 'w') as f:
            json.dump(api_workflow, f, indent=2)
        print(f"✅ Saved API format to: {output_file}")
        print("\n💡 To use this in your handler:")
        print("   1. Copy this file to your Docker image")
        print("   2. Update handler to use this file instead of converting UI format")
    else:
        print("\n💡 Alternative: Export from ComfyUI UI:")
        print("   1. Open ComfyUI in browser")
        print("   2. Load your workflow")
        print("   3. Menu → Workflow → Export (API)")
        print("   4. Save the exported file")
