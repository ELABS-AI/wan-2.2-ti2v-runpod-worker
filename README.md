# elabs / Wan 2.2 Text+Image-to-Video

[![Deploy on RunPod](https://img.shields.io/badge/RunPod-Deploy-orange?logo=runpod)](https://console.runpod.io/hub)
[![CUDA 12.4](https://img.shields.io/badge/CUDA-12.4-green)](https://developer.nvidia.com/cuda-toolkit)
[![Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue)](https://opensource.org/licenses/Apache-2.0)

**Text + Image to Video** with Wan 2.2. Generate videos conditioned on BOTH a text prompt AND a reference image -- the most controlled video generation mode.

![Wan TI2V](https://pub-796a08821c1c483aaf5e274e0d03e350.r2.dev/hub-icons/wan-ti2v.svg)

## Highlights

- Dual conditioning -- text prompt + reference image
- Maximum control -- image defines style, prompt defines motion
- Consistent subject -- maintains reference throughout
- 2-8 second output -- configurable duration and frame rate
- Weights baked in -- fast cold start, no network volume

## Quick Start

```bash
curl -X POST https://api.runpod.ai/v2/{ENDPOINT_ID}/run \
  -H "Authorization: Bearer $RUNPOD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": {"image_base64": "<base64 PNG>", "prompt": "The figure walks forward slowly", "duration_seconds": 4}}'
```

## API

### Input

```json
{
  "input": {
    "image_base64": "<base64 PNG or JPG>",
    "prompt": "The figure walks forward slowly in the scene",
    "duration_seconds": 4,
    "fps": 24,
    "cfg_scale": 7.0,
    "seed": -1
  }
}
```

### Output

```json
{
  "video_base64": "<base64 MP4>",
  "prompt": "The figure walks forward slowly in the scene",
  "duration_s": 4,
  "fps": 24,
  "seed": 99887,
  "wall_time_s": 60.0
}
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `image_base64` | string | required | Reference image (Base64 PNG/JPG) |
| `prompt` | string | required | Motion/action text description |
| `duration_seconds` | float | `4.0` | Video duration (2.0-8.0) |
| `fps` | int | `24` | Frame rate (16 or 24) |
| `cfg_scale` | float | `7.0` | Prompt adherence (1.0-20.0) |
| `seed` | int | `-1` | Seed (-1 = random) |

## I2V vs TI2V Comparison

| Feature | I2V | TI2V |
|---|---|---|
| Conditioning | Image only | Image + Text |
| Motion control | Limited | Full text-guided |
| Best for | Simple animation | Complex directed motion |

## GPU Requirements

- Minimum: >=16GB VRAM
- Recommended: RTX 4090, L40S (>=24GB)
- CUDA: 12.4+

## License

Apache-2.0. Based on [Wan-AI/Wan2.1-T2V](https://huggingface.co/Wan-AI).
