# 🔑 EXACT Environment Variables for RunPod Serverless Worker

## ⚡ REQUIRED - Add These to Your RunPod Endpoint

### 📤 Cloudflare R2 Storage Configuration
```
Variable Name: CF_ACCESS_KEY_ID
Value: your_cloudflare_r2_access_key_here

Variable Name: CF_SECRET_ACCESS_KEY  
Value: your_cloudflare_r2_secret_access_key_here

Variable Name: CF_R2_ENDPOINT_URL
Value: https://your_account_id.r2.cloudflarestorage.com

Variable Name: CF_R2_BUCKET_NAME
Value: your_bucket_name_here
```

### 🤗 HuggingFace Authentication
```
Variable Name: HUGGINGFACE_TOKEN
Value: your_huggingface_token_with_flux_access
```

## ✅ AUTO-CONFIGURED - Built Into Container (No Need to Add)

These are automatically set in the Dockerfile:
```
HF_HUB_ENABLE_HF_TRANSFER=1
GRADIO_ANALYTICS_ENABLED=0
PYTHONIOENCODING=utf-8
LOG_LEVEL=DEBUG
FLUX_MODEL_PATH=/workspace/models/flux/flux1-dev.safetensors
CLIP_MODEL_PATH=/workspace/models/clip/clip_l.safetensors
T5_MODEL_PATH=/workspace/models/clip/t5xxl_fp16.safetensors
VAE_MODEL_PATH=/workspace/models/vae/ae.sft
PYTHONPATH=/workspace/fluxgym/sd-scripts
```

## 📋 RunPod Serverless Setup Instructions

### 1. Create New Serverless Endpoint
1. Go to RunPod → Serverless
2. Click "New Endpoint"

### 2. Container Configuration  
```
Container Image: your-registry/fluxgym-serverless:latest
Container Disk: 100 GB
GPU Type: A100 40GB (or RTX 4090)
```

### 3. Environment Variables Setup
Add ONLY these 5 variables (the required ones):

| Variable Name | Value |
|---------------|-------|
| `CF_ACCESS_KEY_ID` | `your_cloudflare_r2_access_key` |
| `CF_SECRET_ACCESS_KEY` | `your_cloudflare_r2_secret_access_key` |
| `CF_R2_ENDPOINT_URL` | `https://your_account_id.r2.cloudflarestorage.com` |
| `CF_R2_BUCKET_NAME` | `your_bucket_name` |
| `HUGGINGFACE_TOKEN` | `your_huggingface_token` |

### 4. Scaling Configuration
```
Min Workers: 0 (for true serverless)
Max Workers: 3 (adjust based on usage)
Idle Timeout: 5 minutes
Max Execution Time: 2 hours
```

### 5. Test API Call
```json
{
  "input": {
    "character_name": "test_character",
    "trigger_word": "testperson",
    "images": [
      "https://your-r2-bucket/image1.jpg",
      "https://your-r2-bucket/image2.jpg"
    ],
    "epochs": 16
  }
}
```

## 🎯 CRITICAL NOTES

### ✅ WORKING Environment Variables
- Container automatically sets all FluxGym configs
- Only need to provide R2 credentials + HF token
- No need to set model paths manually

### ❌ DON'T Add These (Auto-configured)
- `HF_HUB_ENABLE_HF_TRANSFER` ← Built into container
- `GRADIO_ANALYTICS_ENABLED` ← Built into container  
- `PYTHONPATH` ← Built into container
- Model path variables ← Built into container

### 🔧 First Run Behavior
- Cold start: ~2-5 minutes (model downloads)
- Warm start: ~30 seconds (models cached)
- FLUX model: 23.8GB download on first run
- Text encoders: ~10GB additional download

## 🚀 Ready to Deploy!

Your serverless worker will have:
- ✅ Complete FLUX training pipeline
- ✅ Auto-scaling serverless architecture
- ✅ All missing FluxGym components
- ✅ Production-ready error handling
- ✅ R2 storage integration
