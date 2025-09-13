# SIMPLE WORKING FLUX CONTAINER
FROM runpod/pytorch:2.4.0-py3.10-cuda12.1.1-devel-ubuntu22.04

WORKDIR /workspace

# Install runpod - THAT'S IT
RUN pip install runpod

# Copy handler
COPY handler_fluxgym.py handler_fluxgym.py

# Install basic requirements
RUN pip install transformers diffusers accelerate safetensors huggingface-hub boto3

# Clone FluxGym
RUN git clone https://github.com/cocktailpeanut/fluxgym.git

# Set environment
ENV PYTHONPATH="/workspace/fluxgym"

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
