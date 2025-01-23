import logging
from typing import Optional, Dict
from diffusers import StableDiffusionPipeline
import torch
import os

logger = logging.getLogger(__name__)

class ImageGenerator:
    """Image generation utility using Stable Diffusion."""
    
    def __init__(self, mock_mode: bool = False):
        self.mock_mode = mock_mode
        self._model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.style_enhancers = {
            'professional': ['high quality', 'professional lighting'],
            'casual': ['natural lighting', 'candid'],
            'artistic': ['artistic', 'creative']
        }
        
        self.cultural_elements = {
            'india': ['Indian style', 'vibrant colors', 'traditional Indian elements', 'colorful saree', 'cultural heritage'],
            'korean': ['Korean aesthetic', 'minimalist', 'K-pop style', 'modern Seoul'],
            'nepali': ['Himalayan influence', 'traditional', 'mountain landscape']
        }
        
        logger.info(f"Initialized ImageGenerator with device: {self.device}")

    @property
    def model(self) -> StableDiffusionPipeline:
        """Lazy loading of model."""
        if self._model is None:
            logger.info("Loading Stable Diffusion model")
            self._model = StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                torch_dtype=torch.float32 if self.device == "cpu" else torch.float16,
                safety_checker=None
            ).to(self.device)
        return self._model

    def generate_with_style(
        self,
        prompt: str,
        style: str,
        culture: str,
        output_path: Optional[str] = None,
        num_inference_steps: int = 20
    ) -> Optional[str]:
        """Generate image with specific style and cultural context."""
        if not all([prompt, style, culture]):
            raise ValueError("Prompt, style, and culture must be provided")
        
        # Convert culture to lowercase for case-insensitive matching
        culture_lower = culture.lower()
        
        if style.lower() not in self.style_enhancers:
            raise ValueError(f"Unsupported style: {style}")
        if culture_lower not in self.cultural_elements:
            raise ValueError(f"Unsupported culture: {culture}")
        
        # Provide a default output path if not given
        if output_path is None:
            os.makedirs('generated_images', exist_ok=True)
            output_path = os.path.join('generated_images', f'{culture_lower}_{style.lower()}_image.png')
        
        try:
            logger.info(f"Generating image for style: {style}, culture: {culture}")
            
            if self.mock_mode:
                logger.info("Mock mode: Skipping actual generation")
                return output_path
            
            enhanced_prompt = self._enhance_prompt(prompt, style, culture_lower)
            
            with torch.no_grad():
                image = self.model(
                    enhanced_prompt,
                    num_inference_steps=num_inference_steps,
                    height=512,
                    width=512
                ).images[0]
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            image.save(output_path)
            
            logger.info(f"Successfully generated image: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}", exc_info=True)
            raise

    def _enhance_prompt(self, prompt: str, style: str, culture: str) -> str:
        """Enhance prompt with style and cultural elements."""
        try:
            style_elements = self.style_enhancers.get(style.lower(), [])
            cultural_elements = self.cultural_elements.get(culture, [])
            
            # Combine elements and truncate
            enhanced = f"{prompt}, {', '.join(style_elements)}, {', '.join(cultural_elements)}"
            truncated = ', '.join(enhanced.split(', ')[:10])
            
            logger.debug(f"Enhanced prompt: {truncated}")
            return truncated
        except Exception as e:
            logger.error(f"Error enhancing prompt: {str(e)}", exc_info=True)
            raise

    def __del__(self):
        """Cleanup resources."""
        try:
            if hasattr(self, '_model'):
                del self._model
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            logger.info("Cleaned up ImageGenerator resources")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")