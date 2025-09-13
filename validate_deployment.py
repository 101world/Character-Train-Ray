#!/usr/bin/env python3
"""
Pre-deployment validation script for FluxGym RunPod Serverless Endpoint.
Run this script to validate your deployment configuration before going live.
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_status(message, status, details=None):
    """Print a status message with color coding."""
    if status == "PASS":
        print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")
    elif status == "FAIL":
        print(f"{Colors.RED}❌ {message}{Colors.ENDC}")
        if details:
            print(f"   {Colors.RED}{details}{Colors.ENDC}")
    elif status == "WARN":
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.ENDC}")
        if details:
            print(f"   {Colors.YELLOW}{details}{Colors.ENDC}")
    elif status == "INFO":
        print(f"{Colors.BLUE}ℹ️  {message}{Colors.ENDC}")
        if details:
            print(f"   {Colors.BLUE}{details}{Colors.ENDC}")

def check_environment_variables():
    """Check required environment variables."""
    print(f"\n{Colors.BOLD}🔧 Environment Variables{Colors.ENDC}")
    
    required_vars = [
        "CF_ACCESS_KEY_ID",
        "CF_SECRET_ACCESS_KEY", 
        "CF_R2_ENDPOINT_URL",
        "CF_R2_BUCKET_NAME",
        "HUGGINGFACE_TOKEN"
    ]
    
    optional_vars = [
        "FLUX_MODEL_PATH",
        "CLIP_MODEL_PATH",
        "T5_MODEL_PATH", 
        "VAE_MODEL_PATH"
    ]
    
    all_good = True
    
    for var in required_vars:
        if os.getenv(var):
            print_status(f"{var} configured", "PASS")
        else:
            print_status(f"{var} missing", "FAIL", "This environment variable is required")
            all_good = False
    
    for var in optional_vars:
        if os.getenv(var):
            print_status(f"{var} configured", "PASS")
        else:
            print_status(f"{var} using defaults", "INFO", "Will use default path")
    
    return all_good

def check_python_dependencies():
    """Check Python package dependencies."""
    print(f"\n{Colors.BOLD}📦 Python Dependencies{Colors.ENDC}")
    
    critical_packages = [
        "torch",
        "transformers", 
        "accelerate",
        "boto3",
        "huggingface_hub",
        "safetensors",
        "toml",
        "slugify",
        "bitsandbytes"
    ]
    
    all_good = True
    
    for package in critical_packages:
        try:
            module = importlib.import_module(package)
            version = getattr(module, '__version__', 'unknown')
            print_status(f"{package} v{version}", "PASS")
        except ImportError:
            print_status(f"{package} missing", "FAIL", f"pip install {package}")
            all_good = False
    
    # Check PyTorch GPU support
    try:
        import torch
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0) if gpu_count > 0 else "unknown"
            print_status(f"CUDA available with {gpu_count} GPU(s): {gpu_name}", "PASS")
        else:
            print_status("CUDA not available", "WARN", "GPU training will not work")
            all_good = False
    except Exception as e:
        print_status("PyTorch GPU check failed", "FAIL", str(e))
        all_good = False
    
    return all_good

def check_file_structure():
    """Check required files are present."""
    print(f"\n{Colors.BOLD}📁 File Structure{Colors.ENDC}")
    
    required_files = [
        "handler_fluxgym.py",
        "Dockerfile",
        "requirements.txt",
        "accelerate_config.yaml"
    ]
    
    all_good = True
    
    for file in required_files:
        if Path(file).exists():
            size = Path(file).stat().st_size
            print_status(f"{file} ({size} bytes)", "PASS")
        else:
            print_status(f"{file} missing", "FAIL", "This file is required")
            all_good = False
    
    # Check for tests directory
    if Path("tests").exists():
        test_files = list(Path("tests").glob("test_*.py"))
        print_status(f"Tests directory with {len(test_files)} test files", "PASS")
    else:
        print_status("Tests directory missing", "WARN", "Consider adding tests")
    
    return all_good

def check_kohya_setup():
    """Check Kohya sd-scripts setup."""
    print(f"\n{Colors.BOLD}🔧 Kohya sd-scripts Setup{Colors.ENDC}")
    
    kohya_paths = [
        "/workspace/fluxgym/sd-scripts",
        "./sd-scripts",
        "../sd-scripts"
    ]
    
    kohya_found = False
    for path in kohya_paths:
        script_path = Path(path) / "flux_train_network.py"
        if script_path.exists():
            print_status(f"Kohya scripts found at {path}", "PASS")
            kohya_found = True
            break
    
    if not kohya_found:
        print_status("Kohya sd-scripts not found", "FAIL", 
                    "Clone from: git clone -b sd3 https://github.com/kohya-ss/sd-scripts.git")
        return False
    
    # Check Python path configuration
    try:
        sys.path.insert(0, "/workspace/fluxgym/sd-scripts")
        import library.train_util
        print_status("Kohya library imports work", "PASS")
    except ImportError as e:
        print_status("Kohya library imports failed", "FAIL", str(e))
        return False
    
    return True

def check_accelerate_config():
    """Check accelerate configuration."""
    print(f"\n{Colors.BOLD}🚀 Accelerate Configuration{Colors.ENDC}")
    
    try:
        result = subprocess.run(["accelerate", "config", "--config_file", "accelerate_config.yaml"],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print_status("Accelerate config valid", "PASS")
        else:
            print_status("Accelerate config issues", "WARN", result.stderr)
    except FileNotFoundError:
        print_status("Accelerate command not found", "FAIL", "pip install accelerate")
        return False
    
    return True

def check_model_directories():
    """Check model storage directories."""
    print(f"\n{Colors.BOLD}💾 Model Storage{Colors.ENDC}")
    
    model_dirs = [
        "/workspace/models/flux",
        "/workspace/models/clip", 
        "/workspace/models/vae"
    ]
    
    for dir_path in model_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        if Path(dir_path).exists():
            print_status(f"Model directory {dir_path}", "PASS")
        else:
            print_status(f"Cannot create {dir_path}", "FAIL")
            return False
    
    return True

def run_handler_syntax_check():
    """Check handler script syntax."""
    print(f"\n{Colors.BOLD}🐍 Handler Syntax Check{Colors.ENDC}")
    
    try:
        result = subprocess.run([sys.executable, "-m", "py_compile", "handler_fluxgym.py"],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print_status("Handler syntax valid", "PASS")
            return True
        else:
            print_status("Handler syntax errors", "FAIL", result.stderr)
            return False
    except Exception as e:
        print_status("Handler syntax check failed", "FAIL", str(e))
        return False

def main():
    """Run all validation checks."""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("=" * 60)
    print("  FluxGym RunPod Serverless - Deployment Validation")
    print("=" * 60)
    print(f"{Colors.ENDC}")
    
    checks = [
        ("Environment Variables", check_environment_variables),
        ("Python Dependencies", check_python_dependencies),
        ("File Structure", check_file_structure),
        ("Kohya Setup", check_kohya_setup),
        ("Accelerate Config", check_accelerate_config),
        ("Model Storage", check_model_directories),
        ("Handler Syntax", run_handler_syntax_check)
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print_status(f"{name} check failed with exception", "FAIL", str(e))
            results.append((name, False))
    
    # Summary
    print(f"\n{Colors.BOLD}📊 Validation Summary{Colors.ENDC}")
    print("=" * 40)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print_status(name, status)
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} checks passed{Colors.ENDC}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All checks passed! Ready for deployment.{Colors.ENDC}")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ {total - passed} checks failed. Fix issues before deployment.{Colors.ENDC}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
