"""
SIMPLE FluxGym Handler - Just Works
Input: images + trigger_word + character_name  
Output: trained FLUX LoRA
"""

import runpod
import os
import json
import subprocess
import sys
import uuid
from huggingface_hub import hf_hub_download
import boto3
from botocore.config import Config

def download_flux_model():
    """Download FLUX.1-dev model and all required text encoders"""
    print("Setting up FLUX models and text encoders...")
    
    # Get HuggingFace token from environment
    hf_token = os.getenv('HUGGINGFACE_TOKEN')
    if not hf_token:
        print("Warning: HUGGINGFACE_TOKEN not found. FLUX.1-dev requires a token.")
    
    # Create model directories
    os.makedirs("/workspace/models/unet", exist_ok=True)
    os.makedirs("/workspace/models/clip", exist_ok=True) 
    os.makedirs("/workspace/models/vae", exist_ok=True)
    
    # 1. Download FLUX.1-dev main model (23.8GB)
    flux_model_path = "/workspace/models/unet/flux1-dev.sft"
    if not os.path.exists(flux_model_path):
        print("Downloading FLUX.1-dev model (23.8GB)...")
        from huggingface_hub import hf_hub_download
        hf_hub_download(
            repo_id="black-forest-labs/FLUX.1-dev",
            filename="flux1-dev.sft",
            local_dir="/workspace/models/unet",
            local_dir_use_symlinks=False,
            token=hf_token
        )
        print("FLUX.1-dev model download completed!")
    
    # 2. Download CLIP text encoder
    clip_path = "/workspace/models/clip/clip_l.safetensors"
    if not os.path.exists(clip_path):
        print("Downloading CLIP text encoder...")
        hf_hub_download(
            repo_id="comfyanonymous/flux_text_encoders",
            filename="clip_l.safetensors",
            local_dir="/workspace/models/clip",
            local_dir_use_symlinks=False
        )
        print("CLIP text encoder download completed!")
    
    # 3. Download T5XXL text encoder (large!)
    t5xxl_path = "/workspace/models/clip/t5xxl_fp16.safetensors"
    if not os.path.exists(t5xxl_path):
        print("Downloading T5XXL text encoder...")
        hf_hub_download(
            repo_id="comfyanonymous/flux_text_encoders", 
            filename="t5xxl_fp16.safetensors",
            local_dir="/workspace/models/clip",
            local_dir_use_symlinks=False
        )
        print("T5XXL text encoder download completed!")
    
    # 4. Download VAE (AutoEncoder)
    vae_path = "/workspace/models/vae/ae.sft"
    if not os.path.exists(vae_path):
        print("Downloading VAE...")
        hf_hub_download(
            repo_id="cocktailpeanut/xulf-dev",
            filename="ae.sft", 
            local_dir="/workspace/models/vae",
            local_dir_use_symlinks=False
        )
        print("VAE download completed!")
    
    print("All FLUX models and text encoders ready!")
    return "/workspace/models/unet/flux1-dev.sft"

def upload_to_r2(file_path, object_name):
    """Upload file to Cloudflare R2 storage"""
    try:
        # Get R2 credentials from environment (matching web app variable names)
        access_key = os.getenv('CLOUDFLARE_R2_ACCESS_KEY_ID')
        secret_key = os.getenv('CLOUDFLARE_R2_SECRET_ACCESS_KEY')
        account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID')
        bucket_name = os.getenv('R2_BUCKET_NAME')
        public_url_base = os.getenv('R2_BUCKET_PUBLIC_URL')
        
        if not all([access_key, secret_key, account_id, bucket_name]):
            print("Missing R2 credentials, returning local path")
            return file_path
        
        # Construct R2 endpoint URL
        endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"
        
        # Initialize R2 client
        s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version='s3v4')
        )
        
        # Upload file
        s3_client.upload_file(file_path, bucket_name, object_name)
        
        # Return public URL using the public URL base
        if public_url_base:
            public_url = f"{public_url_base}/{object_name}"
        else:
            public_url = f"https://pub-{account_id}.r2.dev/{object_name}"
        
        print(f"Uploaded to R2: {public_url}")
        return public_url
        
    except Exception as e:
        print(f"R2 upload failed: {e}")
        return file_path

def run_flux_training(job):
    """Simple FLUX training - no complications"""
    
    input_data = job["input"]
    
    # Get parameters
    trigger_word = input_data.get("trigger_word", "person")
    character_name = input_data.get("character_name", "character")
    images = input_data.get("images", [])
    steps = input_data.get("steps", 1000)
    
    if not images:
        return {"error": "No images provided"}
    
    try:
        # Download FLUX model if needed
        model_path = download_flux_model()
        
        # Create training directory
        train_dir = f"/tmp/training_{job['id']}"
        os.makedirs(train_dir, exist_ok=True)
        
        # Download images
        for i, img_url in enumerate(images):
            subprocess.run([
                "wget", "-O", f"{train_dir}/image_{i:03d}.jpg", img_url
            ], check=True)
        
        # Create simple captions
        for i in range(len(images)):
            with open(f"{train_dir}/image_{i:03d}.txt", "w") as f:
                f.write(f"{trigger_word} {character_name}")
        
        # Create dataset.toml file (FluxGym style)
        dataset_config = f"""[[datasets]]
[[datasets.subsets]]
image_dir = "{train_dir}"
num_repeats = 10
class_tokens = "{trigger_word} {character_name}"

[datasets.subsets.image_preprocessing]
resolution = 1024
random_crop = false
"""
        
        with open(f"{train_dir}/dataset.toml", "w") as f:
            f.write(dataset_config)
        
        # Run Kohya training script with accelerate and all required text encoders
        kohya_cmd = [
            "accelerate", "launch",
            "--mixed_precision", "bf16",
            "--num_cpu_threads_per_process", "1",
            "/workspace/fluxgym/sd-scripts/flux_train_network.py",
            "--pretrained_model_name_or_path", model_path,
            "--clip_l", "/workspace/models/clip/clip_l.safetensors",
            "--t5xxl", "/workspace/models/clip/t5xxl_fp16.safetensors", 
            "--ae", "/workspace/models/vae/ae.sft",
            "--cache_latents_to_disk",
            "--save_model_as", "safetensors",
            "--sdpa", "--persistent_data_loader_workers",
            "--max_data_loader_n_workers", "2",
            "--seed", "42",
            "--gradient_checkpointing",
            "--mixed_precision", "bf16",
            "--save_precision", "bf16",
            "--network_module", "networks.lora_flux",
            "--network_dim", "32",
            "--learning_rate", "8e-4",
            "--cache_text_encoder_outputs",
            "--cache_text_encoder_outputs_to_disk",
            "--fp8_base",
            "--highvram",
            "--max_train_epochs", "16",
            "--save_every_n_epochs", "4",
            "--dataset_config", f"{train_dir}/dataset.toml",
            "--output_dir", f"{train_dir}/output",
            "--output_name", character_name,
            "--timestep_sampling", "shift", 
            "--discrete_flow_shift", "3.1582",
            "--model_prediction_type", "raw",
            "--guidance_scale", "1.0",
            "--loss_type", "l2",
            "--optimizer_type", "adamw8bit"
        ]
        
        result = subprocess.run(kohya_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Find the output LoRA file
            output_files = []
            public_urls = []
            
            for root, dirs, files in os.walk(f"{train_dir}/output"):
                for file in files:
                    if file.endswith('.safetensors'):
                        local_path = os.path.join(root, file)
                        output_files.append(local_path)
                        
                        # Generate unique object name for R2
                        unique_id = str(uuid.uuid4())[:8]
                        object_name = f"flux_lora/{character_name}_{trigger_word}_{unique_id}_{file}"
                        
                        # Upload to R2 and get public URL
                        public_url = upload_to_r2(local_path, object_name)
                        public_urls.append(public_url)
            
            return {
                "status": "success",
                "lora_files": output_files,  # Local paths for debugging
                "public_urls": public_urls,  # Public R2 URLs
                "trigger_word": trigger_word,
                "character_name": character_name,
                "training_steps": steps
            }
        else:
            return {
                "error": "Training failed",
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
    except Exception as e:
        return {"error": f"Exception: {str(e)}"}

def handler(job):
    """RunPod serverless handler"""
    return run_flux_training(job)

if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
