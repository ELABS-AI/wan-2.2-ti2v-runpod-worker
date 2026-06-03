FROM runpod/pytorch:2.8.0-py3.11-cuda12.8.1-cudnn-devel-ubuntu22.04
LABEL maintainer="E-Labs AI Studio" description="Wan 2.2 TI2V (model baked)"
ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /workspace
COPY requirements-runpod.txt requirements-runpod.txt
RUN pip install --no-cache-dir -r requirements-runpod.txt
RUN python3 <<EOF
import os, huggingface_hub as h, time
M = "Wan-AI/Wan2.1-T2V-14B"
T = "/models/wan21-t2v"
os.makedirs(T, exist_ok=True)
for attempt in range(5):
    try:
        h.snapshot_download(repo_id=M, local_dir=T)
        print("Done:", len(os.listdir(T)), "files", flush=True)
        break
    except Exception as e:
        print(f"Attempt {attempt+1} failed: {e}", flush=True)
        time.sleep(15 * (attempt + 1))
EOF
COPY handler.py /workspace/handler.py
WORKDIR /workspace
CMD ["python", "-u", "handler.py"]
