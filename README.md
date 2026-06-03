# elabs / Wan 2.2 TI2V

[![Run on RunPod](https://runpod.io/badge/runpod-hub)](https://runpod.io/console/hub)

Wan 2.2 text+image-to-video generates videos conditioned on both a text prompt and an input image. Combines prompt understanding with visual grounding for coherent video generation — weights baked into the Docker image.

## Highlights

- **Text + image conditioning** — prompt-driven video generation grounded in a reference image
- **Configurable duration** — 2–8 seconds with fine-grained fps control
- **CFG scale tuning** — adjust how strongly the model follows the text prompt
- **Seed control** — reproducible generations with fixed seeds
- **Weights baked in** — no HF token, no gated access, no cold-download
- **GPU**: requires ≥16 GB VRAM (RTX 4090, L40S, A6000+)

## API

### Input

```json
{
  "input": {
    "image_base64": "<base64-encoded PNG/JPG input image>",
    "prompt": "a serene mountain lake at sunrise, gentle waves rippling",
    "duration_seconds": 4,
    "fps": 16,
    "height": 480,
    "width": 832,
    "cfg_scale": 5.0,
    "seed": -1
  }
}
```

### Output

```json
{
  "video_base64": "<base64-encoded MP4 video>",
  "prompt": "a serene mountain lake at sunrise, gentle waves rippling",
  "duration_s": 4,
  "fps": 16,
  "seed": 42,
  "wall_time_s": 14.2
}
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `image_base64` | string | **required** | Base64-encoded input image (PNG or JPG) |
| `prompt` | string | **required** | Text prompt describing desired video content |
| `duration_seconds` | int | `4` | Output video length in seconds (2–8) |
| `fps` | int | `16` | Frames per second (8–30) |
| `height` | int | `480` | Output video height (in 16px multiples) |
| `width` | int | `832` | Output video width (in 16px multiples) |
| `cfg_scale` | float | `5.0` | Classifier-free guidance scale (1.0–15.0) |
| `seed` | int | `null` | Fixed seed for reproducibility (`-1` or `null` = random) |

## GPU Requirements

- **Recommended**: RTX 4090 (24 GB) / RTX 6000 Ada (48 GB) / L40S (48 GB)
- **Minimum**: Any GPU with ≥16 GB VRAM (A6000, A6000+, etc.)
- **CUDA**: 12.0+

## Benchmark

| GPU | Resolution | Duration | FPS | Time |
|---|---|---|---|---|
| RTX 4090 | 832×480 | 4s | 16 | ~14s |
| RTX 4090 | 1280×720 | 8s | 24 | ~50s |
| L40S | 1280×720 | 8s | 24 | ~40s |

## License

Apache-2.0 — Wan 2.2 TI2V weights and inference implementation.
