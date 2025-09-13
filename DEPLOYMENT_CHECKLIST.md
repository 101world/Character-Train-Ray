# RunPod Deployment Checklist

**Date**: September 13, 2025  
**Project**: FluxGym FLUX LoRA Training Endpoint  
**Status**: Ready for Production Deployment  

---

## ✅ **Pre-Deployment Checklist**

- [x] **Handler Code**: `handler_fluxgym.py` - Production ready
- [x] **Dockerfile**: Correct PyTorch 2.4.0 base image  
- [x] **Requirements**: All dependencies listed
- [x] **Repository**: Clean, no test files in production
- [x] **Tests**: All 5/5 tests passed (moved to /tests folder)

---

## 🔧 **RunPod Configuration Steps**

### **Step 1: Create Serverless Endpoint**
1. Go to RunPod Dashboard → Serverless
2. Click "New Endpoint"
3. Choose "Build from GitHub"

### **Step 2: Container Settings**
```
Base Image: runpod/pytorch:2.4.0-py3.10-cuda12.1.1-devel-ubuntu22.04
Docker Command: python -u /handler_fluxgym.py
Container Disk: 50GB minimum
```

### **Step 3: GitHub Integration**
```
Repository: https://github.com/101world/Character-Train-Ray.git
Branch: master
Build Command: docker build -t fluxgym-worker .
```

### **Step 4: Environment Variables** 
**⚠️ CRITICAL - Replace with your actual values:**
```
CLOUDFLARE_R2_ACCESS_KEY_ID = your_actual_r2_access_key
CLOUDFLARE_R2_SECRET_ACCESS_KEY = your_actual_r2_secret_key
CLOUDFLARE_ACCOUNT_ID = your_actual_account_id
R2_BUCKET_NAME = your_actual_bucket_name
R2_BUCKET_PUBLIC_URL = https://your-actual-bucket-url.com
```

### **Step 5: Network Settings**
```
Max Workers: 1 (for initial testing)
Idle Timeout: 300 seconds
Execution Timeout: 3600 seconds (1 hour)
GPU Types: RTX 4090, A100, or H100
```

---

## 🧪 **Testing Steps**

### **Step 1: Basic Test**
Send this JSON payload to test the endpoint:
```json
{
  "input": {
    "character_name": "test_character",
    "trigger_word": "hero",
    "images": [
      "https://your-r2-url.com/image1.jpg",
      "https://your-r2-url.com/image2.jpg"
    ],
    "steps": 500,
    "learning_rate": "1e-4"
  }
}
```

### **Step 2: Expected Response**
✅ Success response should include:
- `"status": "success"`
- `"public_urls": [...]` - R2 URLs for LoRA files
- `"trigger_word"` and `"character_name"`
- Training completion confirmation

### **Step 3: Monitor Logs**
Watch for these key events:
- Container startup
- FLUX model download (23.8GB, one-time)
- Image download and caption creation
- Training progress with accelerate
- R2 upload completion

---

## 🚨 **Troubleshooting Guide**

### **Common Issues:**
- **CUDA out of memory** → Use smaller batch size or fewer images
- **R2 upload failed** → Check environment variables
- **Training timeout** → Increase execution timeout or reduce steps
- **Container startup failure** → Verify Dockerfile and requirements

### **Success Indicators:**
- ✅ Container builds without errors
- ✅ FLUX model downloads successfully  
- ✅ Training completes with LoRA output
- ✅ Files upload to R2 storage
- ✅ Public URLs returned in response

---

## 🎯 **Production Deployment**

1. **Deploy endpoint** with above settings
2. **Test with sample data** using test payload
3. **Verify R2 integration** - check files upload
4. **Scale workers** once testing successful
5. **Integrate with your web app** using returned URLs

---

**🎉 Your FluxGym RunPod endpoint is ready for production!**

*Character Images → R2 → FLUX Training → LoRA Model → R2 URLs*
