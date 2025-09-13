#!/usr/bin/env python3
"""
Runtime Dependency Installer
Installs any missing packages when the handler starts
"""

import subprocess
import sys

def install_if_missing(package_name, import_name=None):
    """Install package if not already available"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name} already available")
        return True
    except ImportError:
        print(f"📦 Installing {package_name}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package_name, '--quiet'])
            print(f"✅ {package_name} installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package_name}: {e}")
            return False

def ensure_runtime_deps():
    """Ensure all runtime dependencies are available"""
    print("🔧 Checking runtime dependencies...")
    
    # Critical packages the handler needs
    deps = [
        ('runpod', 'runpod'),
        ('torch', 'torch'),
        ('transformers', 'transformers'),
        ('diffusers', 'diffusers'),
        ('accelerate', 'accelerate'),
        ('safetensors', 'safetensors'),
        ('huggingface-hub', 'huggingface_hub'),
        ('boto3', 'boto3'),
        ('Pillow', 'PIL'),
        ('requests', 'requests'),
        ('datasets', 'datasets'),
        ('peft', 'peft'),
        ('bitsandbytes', 'bitsandbytes'),
        ('tqdm', 'tqdm'),
        ('omegaconf', 'omegaconf'),
        ('opencv-python', 'cv2'),
        ('scipy', 'scipy'),
        ('einops', 'einops'),
        ('tensorboard', 'tensorboard'),
    ]
    
    all_good = True
    for package, import_name in deps:
        if not install_if_missing(package, import_name):
            all_good = False
    
    if all_good:
        print("🎉 All runtime dependencies are ready!")
    else:
        print("⚠️  Some dependencies failed to install")
    
    return all_good

if __name__ == "__main__":
    ensure_runtime_deps()