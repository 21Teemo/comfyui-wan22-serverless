#!/usr/bin/env python3
"""
RunPod Serverless client for ComfyUI WAN 2.2 text-to-video.
Use as a module: run_prompt("your prompt") or as CLI: python runpod_client.py "your prompt"
Loads RUNPOD_API_KEY and RUNPOD_ENDPOINT_ID from .env or environment.
"""
import argparse
import base64
import json
import os
import sys
import time
from typing import Any, Dict, List, Optional

import requests


def _load_dotenv() -> Optional[str]:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for path in (
        os.path.join(script_dir, ".env"),
        os.path.join(os.getcwd(), ".env"),
    ):
        path = os.path.abspath(path)
        if os.path.isfile(path):
            with open(path) as f:
                for line in f:
                    line = line.strip().replace("\r", "")
                    if line and not line.startswith("#") and "=" in line:
                        k, _, v = line.partition("=")
                        v = v.strip().strip("'\"").replace("\r", "").replace("\n", "")
                        k = k.strip()
                        if k and v:
                            os.environ[k] = v
            return path
    return None


_load_dotenv()

API_KEY = os.environ.get("RUNPOD_API_KEY")
ENDPOINT_ID = os.environ.get("RUNPOD_ENDPOINT_ID", "j1i0671zabhwmp")
RUNPOD_API = f"https://api.runpod.ai/v2/{ENDPOINT_ID}" if ENDPOINT_ID else None

DEFAULT_OUTPUT_DIR = "runpod_output"
DEFAULT_STEPS = 20
DEFAULT_CFG = 1.2
DEFAULT_WIDTH = 832
DEFAULT_HEIGHT = 480
DEFAULT_LENGTH = 33

# Default prompts when run with no args (edit these or pass via CLI)
DEFAULT_POSITIVE_PROMPT = "iraKim, 1girl, smiling at camera, golden hour lighting, soft focus"
DEFAULT_NEGATIVE_PROMPT = "blurry, distorted, deformed, bad anatomy, bad quality"


def run_prompt(
    prompt: str,
    negative_prompt: Optional[str] = None,
    seed: Optional[int] = None,
    steps: int = DEFAULT_STEPS,
    cfg: float = DEFAULT_CFG,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    length: int = DEFAULT_LENGTH,
    save_outputs: bool = True,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    poll_interval: int = 5,
    max_wait: int = 600,
) -> Dict[str, Any]:
    """
    Submit a prompt to the RunPod ComfyUI endpoint and wait for result.
    Returns dict with: status, job_id, output (raw), saved_paths (list of saved files), error (if failed).
    """
    if not API_KEY or not RUNPOD_API:
        return {
            "status": "FAILED",
            "error": "RUNPOD_API_KEY (and optionally RUNPOD_ENDPOINT_ID) must be set in .env or environment",
        }

    payload = {
        "input": {
            "prompt": prompt,
            "positive_prompt": prompt,
            "negative_prompt": negative_prompt or "",
            "steps": steps,
            "cfg": cfg,
            "width": width,
            "height": height,
            "length": length,
        }
    }
    if seed is not None:
        payload["input"]["seed"] = seed

    try:
        r = requests.post(
            f"{RUNPOD_API}/run",
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json=payload,
            timeout=30,
        )
        r.raise_for_status()
        result = r.json()
    except requests.exceptions.RequestException as e:
        return {"status": "FAILED", "error": str(e), "response_body": getattr(e.response, "text", None)}

    job_id = result.get("id")
    if not job_id:
        return {"status": "FAILED", "error": "No job id in response", "response": result}

    waited = 0
    while waited < max_wait:
        time.sleep(poll_interval)
        waited += poll_interval
        try:
            status_r = requests.get(
                f"{RUNPOD_API}/status/{job_id}",
                headers={"Authorization": f"Bearer {API_KEY}"},
                timeout=10,
            )
            status_r.raise_for_status()
            status_data = status_r.json()
        except requests.exceptions.RequestException as e:
            return {"status": "FAILED", "job_id": job_id, "error": str(e)}

        job_status = status_data.get("status", "UNKNOWN")
        if job_status == "COMPLETED":
            output = status_data.get("output", {})
            payload_out = output.get("output", output)
            images = payload_out.get("images", output.get("images", []))
            saved_paths: List[str] = []
            if save_outputs and images:
                os.makedirs(output_dir, exist_ok=True)
                for i, img in enumerate(images, 1):
                    fn = img.get("filename", f"output_{i}")
                    data_b64 = img.get("data")
                    if data_b64:
                        path = os.path.join(output_dir, fn)
                        with open(path, "wb") as f:
                            f.write(base64.b64decode(data_b64))
                        saved_paths.append(os.path.abspath(path))
            return {
                "status": "COMPLETED",
                "job_id": job_id,
                "output": output,
                "saved_paths": saved_paths,
            }
        if job_status == "FAILED":
            return {
                "status": "FAILED",
                "job_id": job_id,
                "error": status_data.get("error", "Unknown error"),
                "output": status_data.get("output"),
            }

    return {
        "status": "TIMEOUT",
        "job_id": job_id,
        "error": f"Timed out after {max_wait}s",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a prompt on RunPod ComfyUI WAN 2.2 serverless")
    parser.add_argument("prompt", nargs="?", help="Positive prompt (or use --prompt)")
    parser.add_argument("--prompt", "-p", dest="prompt_opt", help="Positive prompt")
    parser.add_argument("--negative", "-n", help="Negative prompt")
    parser.add_argument("--seed", type=int, default=None, help="Seed (default: random)")
    parser.add_argument("--steps", type=int, default=DEFAULT_STEPS, help=f"Steps (default: {DEFAULT_STEPS})")
    parser.add_argument("--cfg", type=float, default=DEFAULT_CFG, help=f"CFG (default: {DEFAULT_CFG})")
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH, help=f"Width (default: {DEFAULT_WIDTH})")
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT, help=f"Height (default: {DEFAULT_HEIGHT})")
    parser.add_argument("--length", type=int, default=DEFAULT_LENGTH, help=f"Frames (default: {DEFAULT_LENGTH})")
    parser.add_argument("--no-save", action="store_true", help="Do not save outputs to disk")
    parser.add_argument("--output-dir", "-o", default=DEFAULT_OUTPUT_DIR, help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})")
    parser.add_argument("--json", action="store_true", help="Print only JSON result")
    args = parser.parse_args()

    prompt = args.prompt or args.prompt_opt
    if not prompt:
        parser.print_help()
        print("\nExample: python runpod_client.py \"1girl, smiling at camera, golden hour\"")
        return 0

    if not API_KEY:
        print("Error: RUNPOD_API_KEY not set. Use .env or environment.", file=sys.stderr)
        return 1

    result = run_prompt(
        prompt=prompt,
        negative_prompt=args.negative,
        seed=args.seed,
        steps=args.steps,
        cfg=args.cfg,
        width=args.width,
        height=args.height,
        length=args.length,
        save_outputs=not args.no_save,
        output_dir=args.output_dir,
    )

    if args.json:
        # Strip large base64 from output for JSON print
        out = {k: v for k, v in result.items() if k != "output"}
        if "output" in result and result["output"]:
            out["output_keys"] = list(result["output"].keys())
            if "images" in result["output"]:
                out["output_image_count"] = len(result["output"].get("images", []))
        print(json.dumps(out, indent=2))
    else:
        if result["status"] == "COMPLETED":
            print("Completed.")
            if result.get("saved_paths"):
                print("Saved:", *result["saved_paths"], sep="\n  ")
        else:
            print("Failed:", result.get("error", result["status"]), file=sys.stderr)

    return 0 if result["status"] == "COMPLETED" else 1


if __name__ == "__main__":
    sys.exit(main())
