"""
RunPod Serverless Handler for ComfyUI WAN 2.2 Text-to-Video Workflow
"""
import runpod
import subprocess
import time
import requests
import json
import os
import sys
from pathlib import Path

# Paths
COMFYUI_DIR = "/workspace/ComfyUI"
COMFYUI_PORT = 8188
COMFYUI_URL = f"http://localhost:{COMFYUI_PORT}"
WORKFLOW_FILE = "/workspace/ComfyUI/user/default/workflows/iraKim_text_to_video_wan .json"

# Global process handle
comfyui_process = None


def log(message):
    """Log with flush to ensure output appears in RunPod logs"""
    print(message, flush=True)
    sys.stdout.flush()
    sys.stderr.flush()

def start_comfyui():
    """Start ComfyUI server in background with detailed logging"""
    global comfyui_process
    
    log("=== Starting ComfyUI ===")
    
    # Check if already running
    try:
        response = requests.get(COMFYUI_URL, timeout=2)
        if response.status_code == 200:
            log("ComfyUI already running")
            return True
    except Exception as e:
        log(f"ComfyUI not running yet: {e}")
    
    # Verify ComfyUI directory exists
    log(f"Checking ComfyUI directory: {COMFYUI_DIR}")
    if not os.path.exists(COMFYUI_DIR):
        log(f"ERROR: ComfyUI directory not found: {COMFYUI_DIR}")
        log(f"Current directory: {os.getcwd()}")
        if os.path.exists("/workspace"):
            log(f"Workspace contents: {os.listdir('/workspace')[:10]}")
        return False
    
    main_py = os.path.join(COMFYUI_DIR, "main.py")
    log(f"Checking main.py: {main_py}")
    if not os.path.exists(main_py):
        log(f"ERROR: main.py not found in {COMFYUI_DIR}")
        if os.path.exists(COMFYUI_DIR):
            log(f"ComfyUI directory contents: {os.listdir(COMFYUI_DIR)[:10]}")
        return False
    
    # Start ComfyUI
    log("Starting ComfyUI process...")
    try:
        comfyui_process = subprocess.Popen(
            [
                sys.executable, "main.py",
                "--listen", "0.0.0.0",
                "--port", str(COMFYUI_PORT),
                "--disable-smart-memory"
            ],
            cwd=COMFYUI_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Combine stderr into stdout
            text=True,
            bufsize=1  # Line buffered
        )
        log(f"Process started with PID: {comfyui_process.pid}")
    except Exception as e:
        log(f"ERROR: Failed to start ComfyUI process: {e}")
        import traceback
        log(traceback.format_exc())
        return False
    
    # Wait for server to start (max 120 seconds) with progress logging
    log("Waiting for ComfyUI to start (checking every 2 seconds)...")
    for i in range(60):  # 60 * 2 = 120 seconds max
        # Check if process died
        if comfyui_process.poll() is not None:
            log(f"ERROR: ComfyUI process exited with code {comfyui_process.returncode}")
            # Try to read output
            try:
                stdout, _ = comfyui_process.communicate(timeout=2)
                if stdout:
                    log(f"ComfyUI output (last 1000 chars):\n{stdout[-1000:]}")
            except:
                pass
            return False
        
        # Check if server is responding
        try:
            response = requests.get(COMFYUI_URL, timeout=2)
            if response.status_code == 200:
                log(f"✅ ComfyUI started successfully after {i*2} seconds")
                return True
        except:
            pass
        
        # Log progress every 10 seconds
        if i % 5 == 0 and i > 0:
            log(f"Still waiting... ({i*2}s/120s)")
        
        time.sleep(2)
    
    log("ERROR: ComfyUI failed to start within 120 seconds")
    if comfyui_process.poll() is None:
        log("Terminating process...")
        comfyui_process.terminate()
        try:
            comfyui_process.wait(timeout=5)
        except:
            comfyui_process.kill()
    
    return False


def load_workflow():
    """Load workflow JSON and convert to API format"""
    try:
        with open(WORKFLOW_FILE, 'r') as f:
            workflow = json.load(f)
        
        # Convert workflow to API format
        api_prompt = {}
        nodes = workflow.get("nodes", [])
        links = workflow.get("links", [])
        
        # Build link map by link_id for quick lookup
        link_by_id = {}
        for link in links:
            # Link format: [link_id, from_node, from_slot, to_node, to_slot, type]
            link_id = link[0]
            link_by_id[link_id] = {
                "from_node": str(link[1]),
                "from_slot": link[2],
                "to_node": str(link[3]),
                "to_slot": link[4]
            }
        
        # Build reverse map: to_node -> {input_name: [from_node, from_slot]}
        to_node_links = {}
        for link_id, link_info in link_by_id.items():
            to_node = link_info["to_node"]
            if to_node not in to_node_links:
                to_node_links[to_node] = {}
            # We'll match by input order since we don't have input name in link
        
        # Process each node
        for node in nodes:
            node_id = str(node["id"])
            api_prompt[node_id] = {
                "class_type": node["type"],
                "inputs": {}
            }
            
            widgets_values = node.get("widgets_values", [])
            widget_idx = 0
            input_idx = 0  # Track input order for links
            
            # Process inputs in order
            for input_field in node.get("inputs", []):
                input_name = input_field.get("name")
                if not input_name:
                    input_idx += 1
                    continue
                
                # Check if this input has a link
                has_link = False
                if "link" in input_field and input_field["link"] is not None:
                    link_id = input_field["link"]
                    if link_id in link_by_id:
                        link_info = link_by_id[link_id]
                        from_node = link_info["from_node"]
                        from_slot = link_info["from_slot"]
                        api_prompt[node_id]["inputs"][input_name] = [from_node, from_slot]
                        has_link = True
                        log(f"  Node {node_id}.{input_name} -> linked from [{from_node}, {from_slot}]")
                
                # If no link, check if it's a widget
                if not has_link:
                    if "widget" in input_field:
                        if widget_idx < len(widgets_values):
                            value = widgets_values[widget_idx]
                            # Handle special cases
                            if value == "randomize":
                                import random
                                value = random.randint(0, 2**32 - 1)
                            api_prompt[node_id]["inputs"][input_name] = value
                            widget_idx += 1
                            log(f"  Node {node_id}.{input_name} -> widget value: {value}")
                    # If no widget and no link, might be optional - skip it
                
                input_idx += 1
        
        log(f"Converted workflow: {len(api_prompt)} nodes")
        # Validate: check that all nodes have class_type
        for node_id, node_data in api_prompt.items():
            if "class_type" not in node_data:
                log(f"WARNING: Node {node_id} missing class_type")
        
        return api_prompt
    except Exception as e:
        log(f"Error loading workflow: {e}")
        import traceback
        log(traceback.format_exc())
        return None


def update_prompt_params(api_prompt, input_data):
    """Update prompt parameters from input"""
    # Update text prompts
    if "positive_prompt" in input_data:
        # Find CLIPTextEncode node for positive prompt (usually node 6)
        for node_id, node_data in api_prompt.items():
            if node_data.get("class_type") == "CLIPTextEncode":
                if "text" in node_data.get("inputs", {}):
                    api_prompt[node_id]["inputs"]["text"] = input_data["positive_prompt"]
                    break
    
    if "negative_prompt" in input_data:
        # Find CLIPTextEncode node for negative prompt (usually node 7)
        found_positive = False
        for node_id, node_data in api_prompt.items():
            if node_data.get("class_type") == "CLIPTextEncode":
                if not found_positive:
                    found_positive = True
                    continue
                if "text" in node_data.get("inputs", {}):
                    api_prompt[node_id]["inputs"]["text"] = input_data["negative_prompt"]
                    break
    
    # Update seed
    if "seed" in input_data:
        for node_id, node_data in api_prompt.items():
            if node_data.get("class_type") == "KSampler":
                if "seed" in node_data.get("inputs", {}):
                    api_prompt[node_id]["inputs"]["seed"] = input_data["seed"]
    
    # Update steps
    if "steps" in input_data:
        for node_id, node_data in api_prompt.items():
            if node_data.get("class_type") == "KSampler":
                if "steps" in node_data.get("inputs", {}):
                    api_prompt[node_id]["inputs"]["steps"] = input_data["steps"]
    
    # Update CFG
    if "cfg" in input_data:
        for node_id, node_data in api_prompt.items():
            if node_data.get("class_type") == "KSampler":
                if "cfg" in node_data.get("inputs", {}):
                    api_prompt[node_id]["inputs"]["cfg"] = input_data["cfg"]
    
    # Update video dimensions
    if "width" in input_data or "height" in input_data or "length" in input_data:
        for node_id, node_data in api_prompt.items():
            if node_data.get("class_type") == "EmptyHunyuanLatentVideo":
                if "width" in input_data:
                    api_prompt[node_id]["inputs"]["width"] = input_data["width"]
                if "height" in input_data:
                    api_prompt[node_id]["inputs"]["height"] = input_data["height"]
                if "length" in input_data:
                    api_prompt[node_id]["inputs"]["length"] = input_data["length"]
    
    return api_prompt


def queue_prompt(prompt):
    """Queue prompt to ComfyUI"""
    try:
        log(f"Sending prompt with {len(prompt)} nodes")
        # Log first few nodes for debugging
        for i, (node_id, node_data) in enumerate(list(prompt.items())[:3]):
            log(f"  Node {node_id}: {node_data.get('class_type')} - inputs: {list(node_data.get('inputs', {}).keys())}")
        
        response = requests.post(
            f"{COMFYUI_URL}/prompt",
            json={"prompt": prompt},
            timeout=10
        )
        
        if response.status_code != 200:
            error_text = response.text
            log(f"ComfyUI error response ({response.status_code}): {error_text[:500]}")
            try:
                error_json = response.json()
                log(f"Error details: {json.dumps(error_json, indent=2)[:1000]}")
            except:
                pass
            response.raise_for_status()
        
        return response.json()
    except requests.exceptions.HTTPError as e:
        log(f"HTTP Error queueing prompt: {e}")
        if hasattr(e.response, 'text'):
            log(f"Response text: {e.response.text[:1000]}")
        raise
    except Exception as e:
        log(f"Error queueing prompt: {e}")
        import traceback
        log(traceback.format_exc())
        raise


def get_history(prompt_id):
    """Get execution history"""
    try:
        response = requests.get(
            f"{COMFYUI_URL}/history/{prompt_id}",
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting history: {e}")
        return {}


def get_image(filename, subfolder="", folder_type="output"):
    """Download image from ComfyUI"""
    try:
        params = {
            "filename": filename,
            "subfolder": subfolder,
            "type": folder_type
        }
        response = requests.get(f"{COMFYUI_URL}/view", params=params, timeout=30)
        response.raise_for_status()
        return response.content
    except Exception as e:
        log(f"Error getting image: {e}")
        return None


def get_video(filename, subfolder="", folder_type="output"):
    """Download video from ComfyUI"""
    try:
        params = {
            "filename": filename,
            "subfolder": subfolder,
            "type": folder_type
        }
        response = requests.get(f"{COMFYUI_URL}/view", params=params, timeout=60)
        response.raise_for_status()
        return response.content
    except Exception as e:
        log(f"Error getting video: {e}")
        return None


def handler(event):
    """
    Main handler function for RunPod serverless
    """
    log("=== Handler called ===")
    log(f"Event input keys: {list(event.get('input', {}).keys())}")
    
    input_data = event.get("input", {})
    
    # Handle simple "prompt" input (from RunPod quick start)
    if "prompt" in input_data and "positive_prompt" not in input_data:
        log("Converting simple 'prompt' to 'positive_prompt'")
        input_data["positive_prompt"] = input_data.pop("prompt")
    
    # Start ComfyUI if not running
    if not start_comfyui():
        return {
            "error": "Failed to start ComfyUI server",
            "details": "Check logs for startup errors. Common issues: missing dependencies, wrong paths, or ComfyUI crash."
        }
    
    # Load workflow
    log("Loading workflow...")
    api_prompt = load_workflow()
    if not api_prompt:
        return {
            "error": "Failed to load workflow",
            "details": f"Workflow file: {WORKFLOW_FILE}"
        }
    log(f"Workflow loaded with {len(api_prompt)} nodes")
    
    # Update prompt with input parameters
    log("Updating prompt with input parameters...")
    api_prompt = update_prompt_params(api_prompt, input_data)
    
    # Validate prompt before sending
    log("Validating prompt format...")
    for node_id, node_data in api_prompt.items():
        if "class_type" not in node_data:
            return {"error": f"Invalid prompt: node {node_id} missing class_type"}
        if "inputs" not in node_data:
            api_prompt[node_id]["inputs"] = {}
    
    # Queue prompt
    try:
        result = queue_prompt(api_prompt)
        prompt_id = result.get("prompt_id")
        log(f"Prompt queued: {prompt_id}")
    except Exception as e:
        return {"error": f"Failed to queue prompt: {str(e)}"}
    
    # Poll for completion (max 10 minutes)
    max_wait = 600
    waited = 0
    poll_interval = 5
    
    log(f"Waiting for completion (max {max_wait}s)...")
    while waited < max_wait:
        history = get_history(prompt_id)
        
        if prompt_id in history:
            execution = history[prompt_id]
            status = execution.get("status", {})
            
            if status.get("completed", False):
                # Get outputs
                outputs = execution.get("outputs", {})
                videos = []
                images = []
                
                for node_id, node_output in outputs.items():
                    # Check for videos
                    if "videos" in node_output:
                        for vid in node_output["videos"]:
                            video_data = get_video(
                                vid["filename"],
                                vid.get("subfolder", ""),
                                vid.get("type", "output")
                            )
                            if video_data:
                                videos.append({
                                    "filename": vid["filename"],
                                    "data": video_data.hex(),  # Convert to hex for JSON
                                    "size": len(video_data)
                                })
                    
                    # Check for images
                    if "images" in node_output:
                        for img in node_output["images"]:
                            image_data = get_image(
                                img["filename"],
                                img.get("subfolder", ""),
                                img.get("type", "output")
                            )
                            if image_data:
                                images.append({
                                    "filename": img["filename"],
                                    "data": image_data.hex(),
                                    "size": len(image_data)
                                })
                
                return {
                    "status": "completed",
                    "prompt_id": prompt_id,
                    "videos": videos,
                    "images": images,
                    "outputs": outputs
                }
            
            elif status.get("error", False):
                error_msg = status.get("error_message", "Unknown error")
                return {
                    "status": "error",
                    "prompt_id": prompt_id,
                    "error": error_msg
                }
        
        time.sleep(poll_interval)
        waited += poll_interval
        
        if waited % 30 == 0:
            log(f"Still processing... ({waited}s/{max_wait}s)")
    
    return {
        "status": "timeout",
        "prompt_id": prompt_id,
        "error": f"Generation timed out after {max_wait} seconds"
    }


# Start RunPod serverless
if __name__ == "__main__":
    log("=== Starting RunPod handler ===")
    runpod.serverless.start({"handler": handler})
