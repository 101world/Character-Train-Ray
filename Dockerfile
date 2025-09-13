# Working FLUX Training Container
FROM runpod/pytorch:2.4.0-py3.10-cuda12.1.1-devel-ubuntu22.04

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y git wget build-essential && rm -rf /var/lib/apt/lists/*

# Install runpod FIRST (critical!)
RUN pip install runpod

# Clone FluxGym and Kohya BEFORE installing other packages
RUN git clone https://github.com/cocktailpeanut/fluxgym.git
RUN cd fluxgym && git clone -b sd3 https://github.com/kohya-ss/sd-scripts

# Install essential packages for the handler
RUN pip install transformers diffusers accelerate safetensors huggingface-hub boto3 Pillow requests

# Install training dependencies (this is what was missing!)
RUN pip install datasets peft bitsandbytes tqdm omegaconf opencv-python scipy einops tensorboard

# Install Kohya requirements BUT keep runpod safe
RUN cd fluxgym/sd-scripts && pip install --no-deps -r requirements.txt || echo "Some Kohya deps failed, continuing..."

# Make sure runpod is STILL there after everything
RUN pip install --force-reinstall runpod

# Copy handler and dependency checker
COPY handler_fluxgym.py handler_fluxgym.py
COPY ensure_deps.py ensure_deps.py

# Set environment variables
ENV PYTHONPATH="/workspace/fluxgym/sd-scripts:/workspace/fluxgym"
ENV HF_HUB_ENABLE_HF_TRANSFER="1"
ENV GRADIO_ANALYTICS_ENABLED="0"

CMD ["python", "handler_fluxgym.py"]

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
