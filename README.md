# elabs / Wan 2.2 TI2V

Wan 2.2 Text+Image-to-Video (TI2V). Animate any image with a text prompt. Powered by Wan-AI's 14B diffusion model.

[![Docker Build](https://github.com/ELABS-AI/wan-2.2-ti2v-runpod-worker/actions/workflows/build.yml/badge.svg)](https://github.com/ELABS-AI/wan-2.2-ti2v-runpod-worker/actions/workflows/build.yml)

---

## Quick Start

Deploy this worker on [RunPod Serverless](https://www.runpod.io/serverless) using the **Deploy on RunPod** button in the Hub, or manually with the Docker image:

```
ghcr.io/elabs-ai/wan-2.2-ti2v-runpod-worker:latest
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_ID` | `Wan-AI/Wan2.2-TI2V-A14B-Diffusers` | HuggingFace model ID for Wan 2.2 TI2V |
| `HF_HOME` | `/runpod-volume/models/huggingface` | HuggingFace cache directory |
| `HUGGINGFACE_HUB_CACHE` | `/runpod-volume/models/huggingface/hub` | HuggingFace hub cache |
| `PYTORCH_CUDA_ALLOC_CONF` | `expandable_segments:True` | CUDA memory allocator config |
| `HF_TOKEN` | `your_token_here` | HuggingFace token (if model is gated) |

> **Note:** `HF_HOME` and `HUGGINGFACE_HUB_CACHE` should point to a RunPod Network Volume mount path for model caching between runs.

---

## API Reference

### Input

```json
{"input": {"image_b64": "<base64 image>", "prompt": "a cat walking gracefully", "num_frames": 16, "fps": 8}}
```

### Output

```json
{"video_b64": "<base64 MP4>", "wall_time_s": 45.0}
```

---

## Usage Examples

### Python (runpod SDK)

```python
import runpod
import base64

client = runpod.AsyncioEndpointClient("wan-2.2-ti2v-runpod-worker")
result = await client.run({"input": {"image_b64": "<base64 image>", "prompt": "a cat walking gracefully", "num_frames": 16, "fps": 8}})
print(result)
```

### cURL

```bash
curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": {"image_b64": "<base64 image>", "prompt": "a cat walking gracefully", "num_frames": 16, "fps": 8}}'

```

---

## GPU Requirements

L40S / RTX 4090 (48GB VRAM recommended) | ~30-60s per clip | Apache 2.0 license

---

## License

Apache 2.0 — See [LICENSE](LICENSE)

---

## Built by [E-Labs AI](https://www.elabsai.com)

Part of the E-Labs AI Studio serverless model fleet. Visit [elabsai.com](https://www.elabsai.com) to use these models in a hosted UI.
