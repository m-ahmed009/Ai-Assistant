import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import dotenv_values
import os
from time import sleep

# Load environment variables
env_vars = dotenv_values(".env")
API_KEY = env_vars.get("HuggingFaceAPIkey")

# API configuration
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {API_KEY}"}

def open_images(prompt):
    """Open generated images in default image viewer"""
    folder_path = "Data"
    prompt = prompt.replace(" ", "_")
    
    # Create Data directory if it doesn't exist
    os.makedirs(folder_path, exist_ok=True)
    
    # Check for image files
    files = [f for f in os.listdir(folder_path) if f.startswith(prompt) and f.endswith('.jpg')]
    
    if not files:
        print(f"No images found for prompt: {prompt}")
        return
    
    for image_file in sorted(files):
        image_path = os.path.join(folder_path, image_file)
        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)  # Small delay between opening images
        except Exception as e:
            print(f"Error opening {image_path}: {e}")

async def query(payload):
    """Make API request to generate image"""
    try:
        response = await asyncio.to_thread(
            requests.post,
            API_URL,
            headers=headers,
            json=payload,
            timeout=30  # Added timeout
        )
        response.raise_for_status()  # Raise exception for bad status codes
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None

async def generate_images(prompt: str):
    """Generate multiple images asynchronously"""
    tasks = []
    
    # Create payloads with different seeds
    for i in range(4):
        payload = {
            "inputs": prompt,
            "parameters": {
                "quality": "high",
                "sharpness": "high",
                "seed": randint(0, 1000000),
                "num_inference_steps": 50  # Added for better quality
            }
        }
        tasks.append(asyncio.create_task(query(payload)))
    
    # Gather all results
    image_bytes_list = await asyncio.gather(*tasks)
    
    # Save valid images
    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:
            filename = f"Data/{prompt.replace(' ', '_')}{i+1}.jpg"
            try:
                with open(filename, "wb") as f:
                    f.write(image_bytes)
                print(f"Saved image: {filename}")
            except Exception as e:
                print(f"Error saving image {filename}: {e}")

def GenerateImages(prompt: str):
    """Main function to generate and open images"""
    try:
        # Create Data directory if it doesn't exist
        os.makedirs("Data", exist_ok=True)
        
        # Run async generation
        asyncio.run(generate_images(prompt))
        
        # Open the generated images
        open_images(prompt)
        return True
    except Exception as e:
        print(f"Image generation failed: {e}")
        return False

def monitor_generation_requests():
    """Monitor for image generation requests"""
    while True:
        try:
            # Check for request file
            request_file = "Frontend/Files/ImageGeneration.data"
            if not os.path.exists(request_file):
                sleep(1)
                continue
                
            # Read request data
            with open(request_file, "r") as f:
                data = f.read().strip()
            
            # Parse request
            if "," in data:
                prompt, status = data.split(",", 1)
                if status.strip().lower() == "true":
                    print(f"Generating images for: {prompt}")
                    
                    # Process request
                    success = GenerateImages(prompt.strip())
                    
                    # Update status
                    with open(request_file, "w") as f:
                        f.write("False,False")
                    
                    if success:
                        print("Image generation completed successfully")
                    else:
                        print("Image generation failed")
                    
                    # Small delay before next check
                    sleep(2)
            else:
                sleep(1)
        except Exception as e:
            print(f"Error in monitoring loop: {e}")
            sleep(1)

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("Frontend/Files", exist_ok=True)
    os.makedirs("Data", exist_ok=True)
    
    # Start monitoring for requests
    monitor_generation_requests()