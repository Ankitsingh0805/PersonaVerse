import logging
from typing import List, Tuple, Optional
import cv2
import torch
import numpy as np
import os
from diffusers import CogVideoXImageToVideoPipeline

logger = logging.getLogger(__name__)

class VideoGenerator:
    """Video generation and processing utility."""
    
    def __init__(self, mock_mode: bool = False):
        self.mock_mode = mock_mode
        self._processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.style_presets = {
            'professional': {'num_frames': 24, 'height': 256, 'width': 256},
            'creative': {'num_frames': 16, 'height': 224, 'width': 224},
            'casual': {'num_frames': 20, 'height': 240, 'width': 240}
        }
        
        logger.info(f"Initialized VideoGenerator with device: {self.device}")

    @property
    def processor(self) -> CogVideoXImageToVideoPipeline:
        """Lazy loading of processor."""
        if self._processor is None:
            logger.info("Loading VideoGenProcessor")
            self._processor = CogVideoXImageToVideoPipeline.from_pretrained("damo-vilab/text-to-video-ms-1.7b")
        return self._processor

    def generate_with_style(
        self,
        prompt: str,
        style: str,
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """Generate video from text prompt with specific style."""
        if not all([prompt, style]):
            raise ValueError("Prompt and style must be provided")
        
        if style.lower() not in self.style_presets:
            raise ValueError(f"Unsupported style: {style}")
        
       
        if output_path is None:
            os.makedirs('generated_videos', exist_ok=True)
            output_path = os.path.join('generated_videos', f'{style.lower()}_video.mp4')
        
        try:
            logger.info(f"Generating video with style: {style}")
            
            if self.mock_mode:
                logger.info("Mock mode: Skipping actual generation")
                return output_path
            
            style_config = self.style_presets[style.lower()]
            
            inputs = self.processor(
                prompt,
                height=style_config['height'],
                width=style_config['width'],
                num_frames=style_config['num_frames'],
                return_tensors="pt"
            ).to(self.device)
            
            with torch.no_grad():
                video_frames = self.processor.generate(inputs)
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Convert frames to video
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            height, width = video_frames[0].shape[:2]
            out = cv2.VideoWriter(output_path, fourcc, 24, (width, height))
            
            for frame in video_frames:
                frame = (frame * 255).to(torch.uint8).numpy()
                out.write(frame)
            
            out.release()
            
            logger.info(f"Successfully generated video: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating video: {str(e)}", exc_info=True)
            raise

    def __del__(self):
        """Cleanup resources."""
        try:
            if hasattr(self, '_processor'):
                del self._processor
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            logger.info("Cleaned up VideoGenerator resources")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

