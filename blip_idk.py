import torch
from PIL import Image
from transformers import Blip2Processor, Blip2ForConditionalGeneration
import os # For checking file existence

# Initialize ONCE (global variables persist across runs)
processor, model = None, None

def load_model(model_name="Salesforce/blip2-opt-2.7b"):
    """Loads the processor and model if they haven't been loaded yet."""
    global processor, model
    if model is None:  # Only load if not already loaded
        print(f"Loading model: {model_name}...")
        try:
            processor = Blip2Processor.from_pretrained(model_name)
            # Use device_map="auto" for better resource management
            model = Blip2ForConditionalGeneration.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" # Let accelerate handle device placement
                # load_in_8bit=True # Uncomment if memory issues persist and bitsandbytes is installed
            )
            print(f"Model loaded successfully onto device(s): {model.hf_device_map if hasattr(model, 'hf_device_map') else model.device}")
        except Exception as e:
            print(f"Error loading model: {e}")
            # Set to None so it might retry later if the issue was temporary
            processor, model = None, None
            raise # Re-raise the exception to signal failure


def describe_image(image_path: str, prompt: str) -> str:
    """Generates a description for the image using the loaded model."""
    try:
        load_model() # Ensure model is loaded (safe to call multiple times)
        if model is None or processor is None:
             return "Error: Model could not be loaded."

        if not os.path.exists(image_path):
            return f"Error: Image file not found at {image_path}"

        image = Image.open(image_path).convert("RGB")

        # Prepare inputs - move inputs to the model's primary device
        # For device_map="auto", model.device often refers to the first device (e.g., 'cuda:0')
        # Ensure input dtype matches model expectation (float16 on GPU)
        input_dtype = torch.float16 if 'cuda' in str(model.device) else torch.float32
        inputs = processor(
            images=image,
            text=prompt,
            return_tensors="pt"
        ).to(model.device, dtype=input_dtype) # Ensure inputs are on the correct device and dtype

        # Generate description
        generated_ids = model.generate(**inputs, max_new_tokens=50)
        description = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
        return description

    except FileNotFoundError:
        return f"Error: Image file not found at {image_path}"
    except Exception as e:
        return f"An error occurred during description generation: {e}"

if __name__ == "__main__":
    image_to_describe = "images.jpeg"  # <--- CHANGE THIS
    # --- Use a clear, revised prompt ---
    search_prompt = "Question: Generate a concise e-commerce search query for the main clothing item shown. Include type, color, and pattern if applicable. Answer:"

    desc = describe_image(image_to_describe, search_prompt)
    print("-" * 20)
    print(f"Image: {image_to_describe}")
    print(f"Prompt: {search_prompt}")
    print(f"Generated Description: {desc}")
    print("-" * 20)