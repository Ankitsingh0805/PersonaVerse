import logging
from typing import Optional
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech
import torch
import soundfile as sf
import os
from datasets import load_dataset
import numpy as np

logger = logging.getLogger(__name__)

class AudioGenerator:
    """Audio generation utility using Microsoft's SpeechT5."""
    
    def __init__(self, mock_mode: bool = False):
        self.mock_mode = mock_mode
        self._processor = None
        self._model = None
        self._speaker_embeddings = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.voice_styles = {
            'professional': {'speed': 1.0, 'pitch': 1.0},
            'casual': {'speed': 1.1, 'pitch': 1.05},
            'energetic': {'speed': 1.2, 'pitch': 1.1}
        }
        
        logger.info(f"Initialized AudioGenerator with device: {self.device}")

    @property
    def processor(self) -> SpeechT5Processor:
        """Lazy loading of processor."""
        if self._processor is None:
            logger.info("Loading SpeechT5Processor")
            self._processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
        return self._processor

    @property
    def model(self) -> SpeechT5ForTextToSpeech:
        """Lazy loading of model."""
        if self._model is None:
            logger.info("Loading SpeechT5ForTextToSpeech")
            self._model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts").to(self.device)
        return self._model

    @property
    def speaker_embeddings(self) -> torch.Tensor:
        """Lazy loading of speaker embeddings."""
        if self._speaker_embeddings is None:
            logger.info("Loading speaker embeddings")
            embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
            self._speaker_embeddings = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0).to(self.device)
        return self._speaker_embeddings

    def generate_with_style(
        self,
        text: str,
        style: str,
        output_path: Optional[str] = None,
        sampling_rate: int = 16000,
        max_length: int = 600  
    ) -> Optional[str]:
        """Generate audio with specific voice style."""
        if not all([text, style]):
            raise ValueError("Text and style must be provided")
        
        if style.lower() not in self.voice_styles:
            raise ValueError(f"Unsupported style: {style}. Available styles: {list(self.voice_styles.keys())}")
        
        # Provide default output path if not given
        if output_path is None:
            os.makedirs('generated_audio', exist_ok=True)
            output_path = os.path.join('generated_audio', f'{style.lower()}_audio.wav')
        
        try:
            logger.info(f"Generating audio for style: {style}")
            
            if self.mock_mode:
                logger.info("Mock mode: Skipping actual generation")
                return output_path
            
            # Truncate input to max_length
            inputs = self.processor(
                text=text, 
                truncation=True, 
                max_length=max_length, 
                return_tensors="pt"
            ).to(self.device)
            
            with torch.no_grad():
                speech = self.model.generate_speech(
                    inputs["input_ids"],
                    self.speaker_embeddings,
                    vocoder=None
                )
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save audio file
            speech = speech.cpu().numpy()
            sf.write(output_path, speech, sampling_rate)
            
            logger.info(f"Successfully generated audio: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating audio: {str(e)}", exc_info=True)
            raise

    def __del__(self):
        """Cleanup resources."""
        try:
            if hasattr(self, '_model'):
                del self._model
            if hasattr(self, '_processor'):
                del self._processor
            if hasattr(self, '_speaker_embeddings'):
                del self._speaker_embeddings
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            logger.info("Cleaned up AudioGenerator resources")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
