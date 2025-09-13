# OFFICIAL FluxGym Dockerfile (EXACTLY as they do it)
FROM nvidia/cuda:12.2.2-base-ubuntu22.04

# Install system dependencies
RUN apt-get update -y && apt-get install -y \
    python3-pip \
    python3-dev \
    git \
    build-essential

WORKDIR /app

# Clone Kohya sd-scripts EXACTLY as FluxGym does it
RUN git clone -b sd3 https://github.com/kohya-ss/sd-scripts && \
    cd sd-scripts && \
    pip install --no-cache-dir -r ./requirements.txt

# Install FluxGym dependencies
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt

# Install PyTorch for CUDA 12.2 (EXACTLY as FluxGym)
RUN pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu122/torch_stable.html

# Install runpod for serverless
RUN pip install runpod

# Copy our handler
COPY handler_fluxgym.py handler_fluxgym.py

# Clone FluxGym for the actual training logic
RUN git clone https://github.com/cocktailpeanut/fluxgym.git

ENV GRADIO_ANALYTICS_ENABLED="0"
ENV HF_HUB_ENABLE_HF_TRANSFER="1"
ENV PYTHONPATH="/app/sd-scripts:/app/fluxgym"

CMD ["python3", "handler_fluxgym.py"]

# Copy handler
COPY handler_fluxgym.py handler_fluxgym.py

# Set critical environment variables matching FluxGym exactly
ENV HF_HUB_ENABLE_HF_TRANSFER="1"
ENV GRADIO_ANALYTICS_ENABLED="0" 
ENV CUDA_VISIBLE_DEVICES="0"
# Critical FluxGym environment variables (THE MISSING AUTO ONES!)
ENV HF_HUB_ENABLE_HF_TRANSFER="1"
ENV GRADIO_ANALYTICS_ENABLED="0"
ENV PYTHONIOENCODING="utf-8"
ENV LOG_LEVEL="DEBUG"

# Model paths for serverless compatibility
ENV FLUX_MODEL_PATH="/workspace/models/flux/flux1-dev.safetensors"
ENV CLIP_MODEL_PATH="/workspace/models/clip/clip_l.safetensors"
ENV T5_MODEL_PATH="/workspace/models/clip/t5xxl_fp16.safetensors"
ENV VAE_MODEL_PATH="/workspace/models/vae/ae.sft"

# Critical Python paths for Kohya integration  
ENV PYTHONPATH="/workspace/fluxgym/sd-scripts:$PYTHONPATH"

CMD ["python", "handler_fluxgym.py"]
