FROM runpod/pytorch:2.8.0-py3.11-cuda12.8.1-cudnn-devel-ubuntu22.04
LABEL maintainer="E-Labs AI Studio" description="Wan 2.2 TI2V RunPod Worker"
ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /workspace
COPY requirements-runpod.txt requirements-runpod.txt
RUN pip install --no-cache-dir -r requirements-runpod.txt
# Bake model weights
RUN python3 -c "import os,huggingface_hub as h; M='Wan-AI/Wan2.1-T2V-14B'; T='/models/wan21-t2v'; os.makedirs(T,exist_ok=True); h.snapshot_download(repo_id=M,local_dir=T); print('Done:',len(os.listdir(T)),'files',flush=True)"
COPY handler.py /workspace/handler.py
WORKDIR /workspace
CMD ["python", "-u", "handler.py"]
