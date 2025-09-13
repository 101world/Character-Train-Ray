# Simple, clean FLUX training image  
FROM runpod/pytorch:0.7.0-cu1241-torch241-ubuntu2204

WORKDIR /workspace

# Install system deps
RUN apt-get update && apt-get install -y git wget build-essential && rm -rf /var/lib/apt/lists/*

# Install runpod first
RUN pip install runpod

# Clone FluxGym and Kohya (sd3 branch is critical!)
RUN git clone https://github.com/cocktailpeanut/fluxgym.git
RUN cd fluxgym && git clone -b sd3 https://github.com/kohya-ss/sd-scripts

# Install Kohya requirements first (in sd-scripts directory)
RUN cd fluxgym/sd-scripts && pip install -r requirements.txt

# Install FLUX requirements and all missing dependencies
RUN pip install transformers diffusers accelerate safetensors datasets torch torchvision \
    timm Pillow requests tokenizers huggingface-hub boto3 slugify toml peft \
    bitsandbytes gradio

# Install correct PyTorch for CUDA 12.4
RUN pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --force-reinstall

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
