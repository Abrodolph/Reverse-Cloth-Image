import torch
from PIL import Image
from transformers import Blip2Processor, Blip2ForConditionalGeneration
from typing import Optional

class ClothingDescriber:
    def __init__(self, model_name: str = "Salesforce/blip2-opt-2.7b"):
        """
        Initialize BLIP-2 model for clothing description.
        Args:
            model_name: HuggingFace model path (default: BLIP-2 optimized for 2.7B parameters)
        """
        # Device setup (auto-detects GPU/CPU)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float16 if self.device == "cuda" else torch.float32
        
        # Load model and processor
        self.processor = Blip2Processor.from_pretrained(model_name)
        self.model = Blip2ForConditionalGeneration.from_pretrained(
            model_name,
            torch_dtype=self.torch_dtype
        ).to(self.device)

    def describe(
        self, 
        image_path: str, 
        prompt: Optional[str] = "a high-quality photo of",
        max_new_tokens: int = 50
    ) -> str:
        """
        Generate a clothing description from an image.
        Args:
            image_path: Path to the image file
            prompt: Optional prompt to guide description
            max_new_tokens: Length of description (default: 50 tokens)
        Returns:
            str: Generated description (e.g., "red cotton t-shirt with logo")
        """
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert("RGB")
            
            # Process inputs
            inputs = self.processor(
                images=image,
                text=prompt,
                return_tensors="pt"
            ).to(self.device, self.torch_dtype)
            
            # Generate description
            generated_ids = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens
            )
            
            # Decode and clean output
            description = self.processor.batch_decode(
                generated_ids, 
                skip_special_tokens=True
            )[0].strip()
            
            return description
        
        except Exception as e:
            raise RuntimeError(f"Error processing image: {str(e)}")

# Example usage
if __name__ == "__main__":
    # Initialize
    describer = ClothingDescriber()
    
    # Describe an image
    description = describer.describe(
        image_path="C:\Personal\stuff\cloth scraper\images.jpeg",
        prompt="Describe this clothing item for an e-commerce search:"
    )
    print(f"Generated Description: {description}")