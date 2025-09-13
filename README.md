# FluxGym RunPod Serverless Endpoint

**A clean, production-ready FLUX LoRA training endpoint for RunPod serverless deployment.**

## 🎯 What This Does

Train custom FLUX LoRA models for character training using a simple serverless API:
- **Input**: Images + trigger word + character name
- **Output**: Trained FLUX LoRA model (.safetensors)
- **Automatic**: FLUX.1-dev model download (23.8GB) and caching

## 🚀 Quick Deploy

### RunPod Deployment
1. **Build the container** using the `Dockerfile`
2. **Deploy** with your RunPod API key
3. **Send training requests** via the API

### API Usage
```json
{
  "input": {
    "images": ["https://example.com/image1.jpg", "https://example.com/image2.jpg"],
    "trigger_word": "person",
    "character_name": "character_name", 
    "steps": 1000
  }
}
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
