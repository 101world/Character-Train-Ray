# Simple, clean FLUX training image  
FROM runpod/pytorch:0.7.0-cu1241-torch241-ubuntu2204

WORKDIR /workspace

# Install system deps
RUN apt-get update && apt-get install -y git wget && rm -rf /var/lib/apt/lists/*

# Install runpod first
RUN pip install runpod

# Clone FluxGym and Kohya
RUN git clone https://github.com/cocktailpeanut/fluxgym.git
RUN cd fluxgym && git clone -b sd3 https://github.com/kohya-ss/sd-scripts

# Install FLUX requirements and Florence-2 dependencies
RUN pip install transformers diffusers accelerate safetensors datasets torch torchvision xformers \
    timm Pillow requests tokenizers huggingface-hub boto3

# Copy handler
COPY handler_fluxgym.py handler_fluxgym.py

CMD ["python", "handler_fluxgym.py"]
