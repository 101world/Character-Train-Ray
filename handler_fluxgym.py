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
from huggingface_hub import snapshot_download
import boto3
from botocore.config import Config

def download_flux_model():
    """Download FLUX.1-dev model if not already cached"""
    model_path = "/workspace/models/FLUX.1-dev"
    
    if not os.path.exists(model_path):
        print("Downloading FLUX.1-dev model (23.8GB)...")
        os.makedirs("/workspace/models", exist_ok=True)
        
        # Download with HuggingFace Hub
        snapshot_download(
            repo_id="black-forest-labs/FLUX.1-dev",
            local_dir=model_path,
            local_dir_use_symlinks=False
        )
        print("FLUX.1-dev model download completed!")
    else:
        print("FLUX.1-dev model already cached")
    
    return model_path

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
        
        # Run Kohya training script with accelerate
        kohya_cmd = [
            "accelerate", "launch",
            "--num_processes=1",
            "--gpu_ids=all",
            "/workspace/fluxgym/sd-scripts/flux_train_network.py",
            "--pretrained_model_name_or_path", model_path,
            "--train_data_dir", train_dir,
            "--output_dir", f"{train_dir}/output",
            "--max_train_steps", str(steps),
            "--save_every_n_steps", str(steps),
            "--mixed_precision", "bf16",
            "--optimizer_type", "adamw8bit",
            "--learning_rate", "1e-4",
            "--resolution", "1024",
            "--train_batch_size", "1",
            "--network_module", "networks.lora",
            "--network_dim", "32",
            "--network_alpha", "16"
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
