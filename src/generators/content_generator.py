from datetime import datetime
import logging
from typing import Dict, Any
from src.models.character import Character
from src.models.content import Content
from src.utils.text_generation import TextGenerator
from src.utils.image_generation import ImageGenerator
from src.utils.audio_generation import AudioGenerator
from src.utils.video_generation import VideoGenerator

class ContentGenerator:
    def __init__(
        self,
        text_generator: TextGenerator,
        image_generator: ImageGenerator,
        audio_generator: AudioGenerator,
        video_generator: VideoGenerator
    ):
        self.text_generator = text_generator
        self.image_generator = image_generator
        self.audio_generator = audio_generator
        self.video_generator = video_generator
        self.logger = logging.getLogger(__name__)

    def generate_post(self, character: Character) -> Content:
        """Generate a multimodal post for a character."""
        try:
            # Get content idea from character's context
            content_context = character.get_content_idea()
            
            # Generate text
            generated_text = self.text_generator.generate_with_style(
                prompt=content_context['topic'],
                character_traits=character.personality_traits,
                mood=content_context['mood'],
                topic=content_context['topic']
            )
            
            # Generate image
            image_path = self.image_generator.generate_with_style(
                prompt=generated_text,
                style='professional',
                culture=character.location.split(',')[1].strip(),
                output_path=None
            )
            
            # Generate audio
            audio_path = self.audio_generator.generate_with_style(
                text=generated_text,
                style='professional',
                output_path=None
            )
            
            # Generate video
            video_path = self.video_generator.generate_with_style(
                prompt=generated_text,
                style='professional',
                output_path=None
            )
            
            # Create Content object
            post = Content(
                character_name=character.name,
                timestamp=datetime.now(),
                content_type='multimodal',
                content=generated_text,
                mood=content_context['mood'],
                context=str(content_context),
                metadata={
                    'image_path': image_path,
                    'audio_path': audio_path,
                    'video_path': video_path
                },
                hashtags=Content.generate_hashtags(content_context, character.location)
            )
            
            return post
        
        except Exception as e:
            self.logger.error(f"Post generation error: {str(e)}")
            raise