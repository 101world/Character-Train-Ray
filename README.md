# Character-Train: FluxGym RunPod Serverless Endpoint

A complete RunPod serverless endpoint for FLUX LoRA character training using FluxGym integration with Cloudflare R2 storage.

## Overview

This project creates a production-ready RunPod serverless worker that:
- Accepts character images via Cloudflare R2 storage
- Automatically downloads FLUX.1-dev model and text encoders
- Trains custom LoRA using Kohya's sd-scripts (sd3 branch)
- Returns trained model URLs back to R2 storage
- Handles the complete end-to-end workflow seamlessly

## Architecture

```
Character Images → R2 Upload → RunPod Worker → FLUX Training → Trained LoRA → R2 Download URLs
```

### Core Components

- **RunPod Serverless**: PyTorch 2.4.1 + CUDA 12.4.1 container
- **FluxGym Integration**: Complete Kohya sd-scripts setup
- **FLUX.1-dev Model**: Automatic download with HuggingFace authentication
- **Text Encoders**: CLIP-L and T5-XXL for optimal training quality
- **Cloudflare R2**: Secure storage for inputs and outputs
- **Docker Container**: Production-ready with all dependencies

## Quick Start

### 1. Environment Setup

Required environment variables in your RunPod endpoint:

```bash
# Cloudflare R2 Configuration
CF_ACCESS_KEY_ID=your_r2_access_key
CF_SECRET_ACCESS_KEY=your_r2_secret_key
CF_R2_ENDPOINT_URL=https://your_account_id.r2.cloudflarestorage.com
CF_R2_BUCKET_NAME=your_bucket_name

# HuggingFace Authentication
HUGGINGFACE_TOKEN=your_hf_token

# Training Configuration
FLUX_MODEL_PATH=/workspace/models/flux/flux1-dev.safetensors
CLIP_MODEL_PATH=/workspace/models/clip/clip_l.safetensors
T5_MODEL_PATH=/workspace/models/clip/t5xxl_fp16.safetensors
VAE_MODEL_PATH=/workspace/models/vae/ae.sft
```

## 📁 Project Structure

```
Character-Train/
├── Dockerfile              # Container build configuration
├── handler_fluxgym.py      # Main serverless handler
├── README.md               # This documentation
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── CLEANUP_LOG.md         # Cleanup documentation
├── PERFORMANCE_LOG.md     # Complete knowledge base & RAG document
└── .github/               # Development guidelines
```

## 🔧 Technical Implementation

### Features
- **FLUX.1-dev Integration**: Automatic model download and caching
- **LoRA Training**: Uses `flux_train_network.py` from Kohya sd-scripts (sd3 branch)
- **Accelerate Support**: Distributed training with `accelerate launch`
- **PyTorch 2.4.0+**: Full FLUX compatibility
- **Florence-2 Ready**: AI captioning support included

### Key Components
- **Base Image**: `runpod/pytorch:2.4.0-py3.10-cuda12.1.1-devel-ubuntu22.04`
- **Training Script**: `flux_train_network.py` with proper LoRA parameters
- **Model Storage**: `/workspace/models/FLUX.1-dev` (auto-cached)
- **Dependencies**: All required libraries pre-installed

## 🛠️ Local Development

### Setup
```bash
# Clone and setup
git clone <repository>
cd Character-Train
copy .env.example .env
# Edit .env with your credentials

# Activate virtual environment (Windows)
.venv\Scripts\Activate.ps1

# Test locally if needed
python handler_fluxgym.py
```

## 📋 Change History

- **September 13, 2025**: Complete implementation with all critical fixes
- **All 8 critical issues resolved**: PyTorch compatibility, correct training scripts, accelerate support
- **Clean production-ready codebase**: Unnecessary files removed, documented in CLEANUP_LOG.md

## 💡 Usage Tips

1. **First run**: FLUX.1-dev model (23.8GB) downloads automatically
2. **Training time**: Typically 10-30 minutes depending on steps and GPU
3. **Output**: LoRA files saved in `/tmp/training_{job_id}/output/`
4. **Memory**: Requires GPU with sufficient VRAM for FLUX training

## 📚 Documentation

- **[PERFORMANCE_LOG.md](PERFORMANCE_LOG.md)** - Complete knowledge base, technical details, and troubleshooting guide
- **[CLEANUP_LOG.md](CLEANUP_LOG.md)** - Detailed cleanup documentation and file removal history
- **[.github/copilot-instructions.md](.github/copilot-instructions.md)** - AI development guidelines

---

**Ready for production deployment on RunPod!** 🚀
