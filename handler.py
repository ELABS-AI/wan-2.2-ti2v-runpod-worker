"""
RunPod serverless handler for Wan 2.2 TI2V — text + image prompt → video generation.

Architecture:
  - Wan 2.2 text+image-to-video diffusion model
  - Dual conditioning on an input image and a text prompt
  - Produces MP4 video output

Environment (set by RunPod template):
  - RUNPOD_POD_ID       — auto
  - RUNPOD_AI_API_KEY   — auto
  - RUNPOD_GPU_COUNT    — auto

Input schema (via RunPod serverless job):
  {
    "input": {
      "image_base64": "...",        // REQUIRED — base64-encoded input image
      "prompt": "a serene lake",    // REQUIRED — text prompt
      "duration_seconds": 4,        // optional — video length (2-8)
      "fps": 16,                    // optional — frames per second (8-30)
      "height": 480,                // optional — video height
      "width": 832,                 // optional — video width
      "cfg_scale": 5.0,             // optional — CFG guidance scale
      "seed": null                  // optional — random seed (null = random)
    }
  }

Output:
  {
    "video_base64": "<base64-encoded MP4>",
    "prompt": "a serene lake",
    "duration_s": 4,
    "fps": 16,
    "seed": 42,
    "wall_time_s": 14.2
  }
"""

import base64
import os
import random
import time
import traceback
from io import BytesIO

# ── Environment setup ─────────────────────────────────────────────────────────
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

import torch

# ── Model path (baked into image at BUILD TIME) ──────────────────────────────
MODEL_ID = "/models/wan22-ti2v"

# ── Global pipeline (loaded once, reused across jobs) ─────────────────────────
_pipe = None
_device = None


def load_pipeline():
    """Load Wan 2.2 TI2V pipeline once and cache globally."""
    global _pipe, _device
    if _pipe is not None:
        return _pipe, _device

    print("[Cold Start] Loading Wan 2.2 TI2V pipeline...", flush=True)
    t0 = time.time()

    _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32

    print(f"  Device: {_device}, dtype: {dtype}", flush=True)
    print(f"  VRAM: {torch.cuda.get_device_properties(0).total_mem / 1e9:.1f} GB", flush=True)

    # Import and load the Wan TI2V pipeline from local model path
    from diffusers import WanTextToVideoPipeline

    # Wan 2.2 TI2V uses a text-conditioned I2V variant — wrapped in pipeline
    pipe = WanTextToVideoPipeline.from_pretrained(
        MODEL_ID,
        torch_dtype=dtype,
    )

    # Move to GPU
    pipe = pipe.to(_device)

    print(f"[Cold Start] Pipeline ready in {time.time() - t0:.1f}s", flush=True)

    _pipe = pipe
    return _pipe, _device


def video_to_b64(video_frames, fps: int) -> str:
    """Convert a list of PIL Image frames to a base64-encoded MP4 video string."""
    import numpy as np

    try:
        import av
    except ImportError:
        # Fallback: use imageio
        import imageio

        buf = BytesIO()
        with imageio.get_writer(buf, format="mp4", fps=fps, codec="libx264") as writer:
            for frame in video_frames:
                writer.append_data(np.array(frame.convert("RGB")))
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")

    # PyAV path
    buf = BytesIO()
    output = av.open(buf, "w", format="mp4")

    frame = video_frames[0]
    width, height = frame.size
    stream = output.add_stream("libx264", rate=fps)
    stream.width = width
    stream.height = height
    stream.pix_fmt = "yuv420p"

    for img in video_frames:
        img_rgb = img.convert("RGB")
        arr = np.array(img_rgb)
        frame_av = av.VideoFrame.from_ndarray(arr, format="rgb24")
        for packet in stream.encode(frame_av):
            output.mux(packet)

    # Flush remaining packets
    for packet in stream.encode():
        output.mux(packet)

    output.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def run_inference(
    image_base64: str,
    prompt: str = "",
    duration_seconds: int = 4,
    fps: int = 16,
    height: int = 480,
    width: int = 832,
    cfg_scale: float = 5.0,
    seed: int | None = None,
) -> tuple:
    """
    Run Wan 2.2 TI2V inference.
    Returns (list_of_PIL_frames, actual_seed, wall_time_s).
    """
    from PIL import Image

    pipe, device = load_pipeline()

    # Decode input image
    img_bytes = base64.b64decode(image_base64)
    input_image = Image.open(BytesIO(img_bytes)).convert("RGB")

    # Set seed
    if seed is None:
        seed = random.randint(0, 2**31 - 1)
    generator = torch.Generator(device=device).manual_seed(seed)

    num_frames = duration_seconds * fps

    print(f"[Inference] Generating {duration_seconds}s video @ {fps}fps ({num_frames} frames)", flush=True)
    print(f"  size={width}x{height}, cfg={cfg_scale}, seed={seed}", flush=True)
    print(f"  prompt='{prompt[:80]}'", flush=True)

    t_start = time.time()

    with torch.inference_mode():
        frames = pipe(
            image=input_image,
            prompt=prompt or "",
            height=height,
            width=width,
            num_frames=num_frames,
            fps=fps,
            guidance_scale=cfg_scale,
            generator=generator,
            num_images_per_prompt=1,
        ).frames[0]

    wall_time = time.time() - t_start
    print(f"[Done] Generation took {wall_time:.1f}s ({num_frames / wall_time:.1f} fps)", flush=True)

    return frames, seed, wall_time


# ═══════════════════════════════════════════════════════════════════════════════
# RunPod Serverless Handler
# ═══════════════════════════════════════════════════════════════════════════════


def handler(job):
    """
    RunPod serverless handler: text + image → base64 MP4 video.

    Called once per job. The pipeline stays loaded across jobs (global).
    """
    job_input = job.get("input", {})
    image_base64 = job_input.get("image_base64", "")
    prompt = job_input.get("prompt", "")

    if not image_base64:
        return {"error": "Missing required field: image_base64"}
    if not prompt:
        return {"error": "Missing required field: prompt"}

    duration_seconds = int(job_input.get("duration_seconds", 4))
    fps = int(job_input.get("fps", 16))
    height = int(job_input.get("height", 480))
    width = int(job_input.get("width", 832))
    cfg_scale = float(job_input.get("cfg_scale", 5.0))
    seed_raw = job_input.get("seed", None)
    seed = int(seed_raw) if seed_raw is not None else None

    # Validate params
    duration_seconds = max(2, min(8, duration_seconds))
    fps = max(8, min(30, fps))
    height = max(256, min(1080, height // 16 * 16))
    width = max(512, min(1920, width // 16 * 16))
    cfg_scale = max(1.0, min(15.0, cfg_scale))

    try:
        frames, actual_seed, wall_time = run_inference(
            image_base64=image_base64,
            prompt=prompt,
            duration_seconds=duration_seconds,
            fps=fps,
            height=height,
            width=width,
            cfg_scale=cfg_scale,
            seed=seed,
        )

        # Encode as base64 MP4
        print("[Worker] Encoding video as base64 MP4...", flush=True)
        video_b64 = video_to_b64(frames, fps)

        return {
            "video_base64": video_b64,
            "prompt": prompt,
            "duration_s": duration_seconds,
            "fps": fps,
            "seed": actual_seed,
            "wall_time_s": round(wall_time, 1),
        }

    except Exception as exc:
        traceback.print_exc()
        return {
            "error": f"Wan 2.2 TI2V inference failed: {str(exc)}",
            "traceback": traceback.format_exc(),
        }


# ── Entrypoint ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import runpod

    runpod.serverless.start({"handler": handler})
