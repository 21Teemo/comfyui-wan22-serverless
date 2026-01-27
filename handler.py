"""
RunPod Serverless Handler for ComfyUI
Based on official runpod-workers/worker-comfyui pattern
Adapted for custom directory structure:
- /workspace/runpod-slim = ComfyUI installation
- /workspace/iraKim_volume = Network Volume (models)
"""
import runpod
import subprocess
import time
import requests
import json
import os
import sys
import base64
import re
from pathlib import Path
from typing import Dict, Any, Optional, List

# Paths - Updated for new directory structure
COMFYUI_DIR = "/workspace/runpod-slim"
COMFYUI_PORT = 8188
COMFYUI_URL = f"http://localhost:{COMFYUI_PORT}"
DEFAULT_WORKFLOW_FILE = "/workspace/runpod-slim/user/default/workflows/iraKim_text_to_video_wan .json"

# Global process handle
comfyui_process = None


def log(message: str):
    """Log with flush to ensure output appears in RunPod logs"""
    print(message, flush=True)
    sys.stdout.flush()
    sys.stderr.flush()


def start_comfyui() -> bool:
    """Start ComfyUI server in background"""
    global comfyui_process

    log("=== Starting ComfyUI ===")

    # Check if already running
    try:
        response = requests.get(COMFYUI_URL, timeout=2)
        if response.status_code == 200:
            log("✅ ComfyUI already running")
            return True
    except Exception:
        pass

    # Verify ComfyUI directory exists
    if not os.path.exists(COMFYUI_DIR):
        log(f"❌ ERROR: ComfyUI directory not found: {COMFYUI_DIR}")
        if os.path.exists("/workspace"):
            log(f"Workspace contents: {os.listdir('/workspace')[:10]}")
        return False

    main_py = os.path.join(COMFYUI_DIR, "main.py")
    if not os.path.exists(main_py):
        log(f"❌ ERROR: main.py not found in {COMFYUI_DIR}")
        return False

    # Setup models symlink from network volume
    # The actual models are at: /workspace/iraKim_volume/comfyui/models
    # ComfyUI expects them at: /workspace/runpod-slim/models
    # So we create a symlink: /workspace/runpod-slim/models -> /workspace/iraKim_volume/comfyui/models
    
    network_models_paths = [
        "/workspace/iraKim_volume/comfyui/models",  # Actual location
        "/workspace/iraKim_volume/models",  # Alternative
        "/workspace/ira_kim_volume/comfyui/models",  # Alternative naming
        "/workspace/ira_kim_volume/models",  # Alternative
    ]
    
    network_models = None
    for vol_path in network_models_paths:
        if os.path.exists(vol_path):
            # Verify it has model subdirectories
            has_models = False
            for subdir in ["text_encoders", "vae", "diffusion_models", "loras"]:
                if os.path.exists(os.path.join(vol_path, subdir)):
                    has_models = True
                    break
            if has_models:
                network_models = vol_path
                log(f"📦 Network volume models found at: {network_models}")
                break
    
    # ComfyUI expects models at: /workspace/runpod-slim/models
    comfyui_models = os.path.join(COMFYUI_DIR, "models")
    
    if network_models:
        # Create symlink: /workspace/runpod-slim/models -> /workspace/iraKim_volume/comfyui/models
        if os.path.exists(comfyui_models) and not os.path.islink(comfyui_models):
            log(f"Removing existing models directory: {comfyui_models}")
            import shutil
            shutil.rmtree(comfyui_models)
        
        if not os.path.exists(comfyui_models) or not os.path.islink(comfyui_models):
            log(f"Creating symlink: {comfyui_models} -> {network_models}")
            try:
                os.symlink(network_models, comfyui_models)
                log(f"✅ Symlink created successfully")
            except Exception as e:
                log(f"❌ Failed to create symlink: {e}")
                import traceback
                log(traceback.format_exc())
        else:
            existing_link = os.readlink(comfyui_models)
            if existing_link != network_models:
                log(f"⚠️  Symlink exists but points to different location: {existing_link}")
                log(f"   Expected: {network_models}")
            else:
                log(f"✅ Symlink already exists: {comfyui_models} -> {network_models}")

        # Verify model subdirectories are accessible
        log(f"📋 Verifying model files:")
        for subdir in ["text_encoders", "vae", "diffusion_models", "loras"]:
            model_path = os.path.join(comfyui_models, subdir)
            if os.path.exists(model_path):
                files = [f for f in os.listdir(model_path) if f.endswith(('.safetensors', '.ckpt', '.pt', '.pth'))]
                log(f"  {subdir}: {len(files)} model files")
                if len(files) > 0:
                    log(f"    Examples: {files[:3]}")
                else:
                    log(f"    ⚠️  WARNING: No model files found in {subdir}")
            else:
                log(f"  ⚠️  WARNING: {subdir} directory not found at {model_path}")
    else:
        log(f"❌ ERROR: Network volume models directory not found")
        log(f"   Checked paths: {network_models_paths}")
        log(f"   ComfyUI will look in: {comfyui_models} (which may be empty)")
        log(f"   This will cause 'value_not_in_list' errors for all model loaders")

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
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        log(f"Process started with PID: {comfyui_process.pid}")
    except Exception as e:
        log(f"❌ ERROR: Failed to start ComfyUI process: {e}")
        import traceback
        log(traceback.format_exc())
        return False

    # Wait for server to start (max 120 seconds)
    log("Waiting for ComfyUI to start...")
    for i in range(60):  # 60 * 2 = 120 seconds max
        if comfyui_process.poll() is not None:
            log(f"❌ ERROR: ComfyUI process exited with code {comfyui_process.returncode}")
            try:
                stdout, _ = comfyui_process.communicate(timeout=2)
                if stdout:
                    log(f"ComfyUI output (last 1000 chars):\n{stdout[-1000:]}")
            except:
                pass
            return False

        try:
            response = requests.get(COMFYUI_URL, timeout=2)
            if response.status_code == 200:
                log(f"✅ ComfyUI started successfully after {i*2} seconds")
                return True
        except:
            pass

        if i % 5 == 0 and i > 0:
            log(f"Still waiting... ({i*2}s/120s)")

        time.sleep(2)

    log("❌ ERROR: ComfyUI failed to start within 120 seconds")
    if comfyui_process.poll() is None:
        comfyui_process.terminate()
    return False


def upload_input_images(images: List[Dict[str, str]]) -> Dict[str, str]:
    """
    Upload input images to ComfyUI's input directory.
    Returns a mapping of image names to their filenames in ComfyUI.
    """
    if not images:
        return {}

    input_dir = os.path.join(COMFYUI_DIR, "input")
    os.makedirs(input_dir, exist_ok=True)

    image_map = {}
    for img_data in images:
        name = img_data.get("name")
        image_data = img_data.get("image", "")

        if not name or not image_data:
            continue

        # Handle data URI format (data:image/png;base64,...)
        if "," in image_data:
            image_data = image_data.split(",", 1)[1]

        try:
            # Decode base64
            image_bytes = base64.b64decode(image_data)
            
            # Determine file extension from name or default to png
            ext = os.path.splitext(name)[1] or ".png"
            if not ext.startswith("."):
                ext = "." + ext
            
            # Save to input directory
            filename = name if name.endswith(ext) else name + ext
            filepath = os.path.join(input_dir, filename)
            
            with open(filepath, "wb") as f:
                f.write(image_bytes)
            
            image_map[name] = filename
            log(f"✅ Uploaded input image: {name} -> {filename}")
        except Exception as e:
            log(f"⚠️  WARNING: Failed to upload image {name}: {e}")

    return image_map


def get_workflow_from_input(input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Get workflow from input. If not provided, try to load default workflow.
    Also supports simple prompt input that updates the default workflow.
    """
    # Check if workflow is provided in input
    if "workflow" in input_data:
        workflow = input_data["workflow"]
        log("Using workflow from API request")
        return workflow

    # Try to load default workflow file
    workflow_file = DEFAULT_WORKFLOW_FILE
    log(f"Checking for default workflow at: {workflow_file}")
    log(f"File exists: {os.path.exists(workflow_file)}")
    
    if not os.path.exists(workflow_file):
        # Try alternative paths
        alt_paths = [
            "/workspace/runpod-slim/user/default/workflows/iraKim_text_to_video_wan .json",
            "/workspace/ComfyUI/user/default/workflows/iraKim_text_to_video_wan .json",
            os.path.join(COMFYUI_DIR, "user/default/workflows/iraKim_text_to_video_wan .json")
        ]
        for alt_path in alt_paths:
            if os.path.exists(alt_path):
                log(f"Found workflow at alternative path: {alt_path}")
                workflow_file = alt_path
                break
        else:
            log(f"❌ ERROR: Default workflow file not found at any path")
            log(f"   Checked: {DEFAULT_WORKFLOW_FILE}")
            log(f"   Also checked: {alt_paths}")
            log(f"   ComfyUI dir exists: {os.path.exists(COMFYUI_DIR)}")
            if os.path.exists(COMFYUI_DIR):
                log(f"   ComfyUI dir contents: {os.listdir(COMFYUI_DIR)[:10]}")
            return None
    
    log(f"Loading default workflow from: {workflow_file}")
    try:
        with open(workflow_file, 'r') as f:
            workflow_data = json.load(f)
        
        # Convert UI workflow format to API format if needed
        if "nodes" in workflow_data:
            # This is UI format, need to convert
            log("Converting UI workflow format to API format...")
            api_workflow = convert_ui_workflow_to_api(workflow_data)
            
            # Update prompt if provided in input
            if "prompt" in input_data:
                prompt_text = input_data["prompt"]
                log(f"Updating prompt in workflow: {prompt_text[:100]}...")
                # Find CLIPTextEncode nodes and update the first one (positive prompt)
                for node_id, node_data in api_workflow.items():
                    if node_data.get("class_type") == "CLIPTextEncode":
                        if "text" in node_data.get("inputs", {}):
                            api_workflow[node_id]["inputs"]["text"] = prompt_text
                            log(f"Updated prompt in node {node_id}")
                            break
            
            return api_workflow
        else:
            # Already in API format
            return workflow_data
    except Exception as e:
        log(f"❌ ERROR: Failed to load default workflow: {e}")
        import traceback
        log(traceback.format_exc())
        return None


def convert_ui_workflow_to_api(workflow: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert ComfyUI UI workflow format to API format.
    This is a simplified version - for complex workflows, use Export (API) in ComfyUI.
    """
    api_prompt = {}
    nodes = workflow.get("nodes", [])
    links = workflow.get("links", [])

    # Build link map: link_id -> {from_node, from_slot, to_node, to_slot}
    link_by_id = {}
    for link in links:
        if len(link) >= 5:
            link_id = link[0]
            link_by_id[link_id] = {
                "from_node": str(link[1]),
                "from_slot": link[2],
                "to_node": str(link[3]),
                "to_slot": link[4]
            }

    # Build reverse map: to_node -> list of inputs that have links
    to_node_inputs = {}
    for link_id, link_info in link_by_id.items():
        to_node = link_info["to_node"]
        if to_node not in to_node_inputs:
            to_node_inputs[to_node] = []
        to_node_inputs[to_node].append({
            "link_id": link_id,
            "from_node": link_info["from_node"],
            "from_slot": link_info["from_slot"],
            "to_slot": link_info["to_slot"]
        })

    # Process each node
    for node in nodes:
        node_id = str(node["id"])
        api_prompt[node_id] = {
            "class_type": node["type"],
            "inputs": {}
        }

        widgets_values = node.get("widgets_values", [])
        widget_idx = 0

        # Process inputs in order
        for input_field in node.get("inputs", []):
            input_name = input_field.get("name")
            if not input_name:
                continue

            # Check for link first
            if "link" in input_field and input_field["link"] is not None:
                link_id = input_field["link"]
                if link_id in link_by_id:
                    link_info = link_by_id[link_id]
                    api_prompt[node_id]["inputs"][input_name] = [
                        link_info["from_node"],
                        link_info["from_slot"]
                    ]
                    continue
                else:
                    log(f"  WARNING: Node {node_id}.{input_name} has link {link_id} but link not found in link_by_id")

            # Check for widget value (only if no link)
            if "widget" in input_field:
                if widget_idx < len(widgets_values):
                    value = widgets_values[widget_idx]
                    
                    # Handle special widget types and conversions
                    if isinstance(value, str) and value == "randomize":
                        # For seed, use random; for steps, cap at 10000
                        if input_name == "seed":
                            import random
                            value = random.randint(0, 2**32 - 1)
                        elif input_name == "steps":
                            value = 20  # Default steps
                    
                    # Fix KSampler widget values
                    if node.get("type") == "KSampler":
                        if input_name == "denoise":
                            # Convert string "simple" to float 1.0
                            if isinstance(value, str):
                                if value == "simple":
                                    value = 1.0
                                else:
                                    try:
                                        value = float(value)
                                    except:
                                        value = 1.0
                                log(f"  Converted denoise '{widgets_values[widget_idx]}' to {value}")
                        elif input_name == "scheduler":
                            # Fix invalid scheduler values
                            valid_schedulers = ["simple", "sgm_uniform", "karras", "exponential", "ddim_uniform", 
                                               "beta", "normal", "linear_quadratic", "kl_optimal"]
                            if value not in valid_schedulers:
                                log(f"  WARNING: Invalid scheduler '{value}', using 'simple'")
                                value = "simple"
                        elif input_name == "sampler_name":
                            # Convert integer index to sampler name string
                            if isinstance(value, int):
                                sampler_names = [
                                    "euler", "euler_ancestral", "heun", "heunpp2", "dpm_2", "dpm_2_ancestral",
                                    "lms", "dpm_fast", "dpm_adaptive", "dpmpp_2s_ancestral", "dpmpp_sde", 
                                    "dpmpp_sde_gpu", "dpmpp_2m", "dpmpp_2m_sde", "dpmpp_2m_sde_gpu", 
                                    "dpmpp_2m_sde_heun", "dpmpp_2m_sde_heun_gpu", "dpmpp_3m_sde", "dpmpp_3m_sde_gpu",
                                    "ddpm", "lcm", "ddim", "uni_pc", "uni_pc_bh2"
                                ]
                                if 0 <= value < len(sampler_names):
                                    value = sampler_names[value]
                                    log(f"  Converted sampler_name index {widgets_values[widget_idx]} to '{value}'")
                                else:
                                    log(f"  WARNING: sampler_name index {value} out of range, using 'euler'")
                                    value = "euler"
                    
                    api_prompt[node_id]["inputs"][input_name] = value
                    widget_idx += 1
                else:
                    log(f"  WARNING: Node {node_id}.{input_name} has widget but no value at index {widget_idx}")
            
            # If input has neither link nor widget, it might be optional
            # But log it for debugging
            if "link" not in input_field or input_field.get("link") is None:
                if "widget" not in input_field:
                    log(f"  INFO: Node {node_id}.{input_name} has no link and no widget (likely optional)")

    log(f"Converted workflow: {len(api_prompt)} nodes")
    
    # Log summary of inputs per node for debugging
    for node_id, node_data in api_prompt.items():
        input_count = len(node_data.get("inputs", {}))
        class_type = node_data.get("class_type", "unknown")
        log(f"  Node {node_id} ({class_type}): {input_count} inputs")
        if input_count == 0:
            log(f"    ⚠️  WARNING: Node {node_id} has no inputs!")
    
    return api_prompt


def queue_prompt(prompt: Dict[str, Any]) -> Dict[str, Any]:
    """Queue prompt to ComfyUI"""
    try:
        response = requests.post(
            f"{COMFYUI_URL}/prompt",
            json={"prompt": prompt},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                error_msg = json.dumps(error_detail, indent=2)
                # Log full error details
                log(f"❌ ComfyUI validation error:")
                log(f"   {error_msg}")
                # Try to extract node errors if present
                if isinstance(error_detail, dict):
                    if "error" in error_detail:
                        error_info = error_detail["error"]
                        if isinstance(error_info, dict) and "node_errors" in error_info:
                            log(f"   Node errors:")
                            for node_id, node_error in error_info["node_errors"].items():
                                log(f"     Node {node_id}: {node_error}")
            except:
                error_msg = e.response.text[:2000]
                log(f"❌ ComfyUI error response: {error_msg}")
        log(f"❌ Error queueing prompt: {error_msg}")
        raise
    except Exception as e:
        log(f"❌ Error queueing prompt: {e}")
        import traceback
        log(traceback.format_exc())
        raise


def get_history(prompt_id: str) -> Dict[str, Any]:
    """Get execution history"""
    try:
        response = requests.get(
            f"{COMFYUI_URL}/history/{prompt_id}",
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        log(f"⚠️  Error getting history: {e}")
        return {}


def get_image(filename: str, subfolder: str = "", folder_type: str = "output") -> Optional[bytes]:
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
        log(f"⚠️  Error getting image {filename}: {e}")
        return None


def get_video(filename: str, subfolder: str = "", folder_type: str = "output") -> Optional[bytes]:
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
        log(f"⚠️  Error getting video {filename}: {e}")
        return None


def handler(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main handler function for RunPod serverless
    Follows official worker-comfyui API format:
    - input.workflow: Workflow JSON (API format)
    - input.images: Optional array of input images (base64)
    """
    log("=== Handler called ===")
    
    input_data = event.get("input", {})
    log(f"Input keys: {list(input_data.keys())}")

    # Start ComfyUI if not running
    if not start_comfyui():
        return {
            "error": "Failed to start ComfyUI server",
            "details": "Check logs for startup errors"
        }

    # Get workflow
    workflow = get_workflow_from_input(input_data)
    if not workflow:
        return {
            "error": "No workflow provided",
            "details": "Provide workflow in input.workflow or ensure default workflow file exists"
        }

    # Upload input images if provided
    input_images = input_data.get("images", [])
    image_map = upload_input_images(input_images)

    # Log workflow structure for debugging
    log(f"Workflow structure: {len(workflow)} nodes")
    for node_id, node_data in list(workflow.items())[:5]:  # Log first 5 nodes
        class_type = node_data.get("class_type", "unknown")
        inputs = node_data.get("inputs", {})
        log(f"  Node {node_id} ({class_type}): {len(inputs)} inputs - {list(inputs.keys())[:3]}")
    
    # Queue prompt
    try:
        result = queue_prompt(workflow)
        prompt_id = result.get("prompt_id")
        log(f"✅ Prompt queued: {prompt_id}")
    except Exception as e:
        # Log the workflow that failed for debugging
        log(f"❌ Failed workflow structure:")
        for node_id, node_data in workflow.items():
            log(f"  Node {node_id}: {node_data.get('class_type')} - inputs: {list(node_data.get('inputs', {}).keys())}")
        return {
            "error": "Failed to queue prompt",
            "details": str(e)
        }

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
                output_images = []

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
                                # Convert to base64
                                video_b64 = base64.b64encode(video_data).decode('utf-8')
                                output_images.append({
                                    "filename": vid["filename"],
                                    "type": "base64",
                                    "data": video_b64
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
                                # Convert to base64
                                image_b64 = base64.b64encode(image_data).decode('utf-8')
                                output_images.append({
                                    "filename": img["filename"],
                                    "type": "base64",
                                    "data": image_b64
                                })

                return {
                    "id": prompt_id,
                    "status": "COMPLETED",
                    "output": {
                        "images": output_images
                    }
                }

            elif status.get("error", False):
                error_msg = status.get("error_message", "Unknown error")
                return {
                    "id": prompt_id,
                    "status": "FAILED",
                    "error": error_msg
                }

        time.sleep(poll_interval)
        waited += poll_interval

        if waited % 30 == 0:
            log(f"Still processing... ({waited}s/{max_wait}s)")

    return {
        "id": prompt_id,
        "status": "TIMEOUT",
        "error": f"Generation timed out after {max_wait} seconds"
    }


# Start RunPod serverless
if __name__ == "__main__":
    log("=== Starting RunPod handler ===")
    runpod.serverless.start({"handler": handler})
