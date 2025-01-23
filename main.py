import yaml
import logging
import time
from datetime import datetime
import argparse
import os
from typing import Dict, List
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from src.models.character import Character, DailyRoutine, ContentPreferences
from src.generators.content_generator import ContentGenerator
from src.generators.character_generator import CharacterGenerator
from src.utils.text_generation import TextGenerator
from src.utils.image_generation import ImageGenerator
from src.utils.audio_generation import AudioGenerator
from src.utils.video_generation import VideoGenerator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('character_simulation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AICharacterSimulation:
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the AI character simulation system."""
        self.config = self.load_config(config_path)
        self.character_generator = CharacterGenerator()
        
        # Initialize all generation models
        logger.info("Initializing generation models...")
        self.init_generators()
        
        self.characters = {}
        logger.info("AI Character Simulation initialized successfully")

    def load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            raise

    def init_generators(self):
        """Initialize all content generation models."""
        try:
            # Text generation
            model_name = self.config['models']['text_generation']
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True,
                device_map='auto' if torch.cuda.is_available() else None
            )
            self.text_generator = TextGenerator(model, tokenizer)
            logger.info(f"Text generator initialized with model: {model_name}")

            # Initialize other generators
            self.image_generator = ImageGenerator()
            logger.info("Image generator initialized")
            
            self.audio_generator = AudioGenerator()
            logger.info("Audio generator initialized")
            
            self.video_generator = VideoGenerator()
            logger.info("Video generator initialized")

            # Initialize content generator with all generation capabilities
            self.content_generator = ContentGenerator(
                text_generator=self.text_generator,
                image_generator=self.image_generator,
                audio_generator=self.audio_generator,
                video_generator=self.video_generator
            )
            
        except Exception as e:
            logger.error(f"Error initializing generators: {str(e)}")
            raise

    def create_characters(self):
        """Create AI characters for different regions."""
        try:
            # Create Indian character
            indian_character = self.character_generator.generate_character(
                region='India',
                age_range=(23, 28),
                occupation_category='tech'
            )
            self.characters['indian'] = indian_character
            logger.info(f"Created Indian character: {indian_character.name}")

            # Create Korean character
            korean_character = self.character_generator.generate_character(
                region='South Korea',
                age_range=(24, 29),
                occupation_category='creative'
            )
            self.characters['korean'] = korean_character
            logger.info(f"Created Korean character: {korean_character.name}")

        except Exception as e:
            logger.error(f"Error creating characters: {str(e)}")
            raise

    def simulate_character_activity(
        self,
        character_id: str,
        duration_hours: float = 24.0,
        post_interval_minutes: float = 60.0
    ):
        """Simulate character activity for specified duration."""
        if character_id not in self.characters:
            raise ValueError(f"Character {character_id} not found")
        
        character = self.characters[character_id]
        start_time = datetime.now()
        post_interval = post_interval_minutes * 60  # Convert to seconds
        last_post_time = start_time
        
        logger.info(f"Starting simulation for {character.name} for {duration_hours} hours")
        
        try:
            while (datetime.now() - start_time).total_seconds() < duration_hours * 3600:
                current_time = datetime.now()
                
                # Check if it's time for a new post
                if (current_time - last_post_time).total_seconds() >= post_interval:
                    # Generate and display post
                    post = self.content_generator.generate_post(character)
                    
                    # Log post details
                    logger.info(f"\n{'='*50}")
                    logger.info(f"New post from {character.name} ({post.timestamp})")
                    logger.info(f"Current activity: {post.context}")
                    logger.info(f"Mood: {post.mood}")
                    logger.info(f"Content type: {post.content_type}")
                    logger.info(f"\nContent:\n{post.content}")
                    
                    # Log media content if present
                    if hasattr(post, 'image_path') and post.image_path:
                        logger.info(f"Image generated: {post.image_path}")
                    if hasattr(post, 'audio_path') and post.audio_path:
                        logger.info(f"Audio generated: {post.audio_path}")
                    if hasattr(post, 'video_path') and post.video_path:
                        logger.info(f"Video generated: {post.video_path}")
                    
                    logger.info(f"\nHashtags: {' '.join(post.hashtags)}")
                    
                    # Save post to file
                    self.save_post(post, character_id)
                    
                    last_post_time = current_time
                
                # Sleep to prevent high CPU usage
                time.sleep(10)
                
        except KeyboardInterrupt:
            logger.info("Simulation interrupted by user")
        except Exception as e:
            logger.error(f"Error during simulation: {str(e)}")
            raise
        finally:
            logger.info(f"Simulation ended for {character.name}")

    def save_post(self, post, character_id: str):
        """Save generated post and associated media to files."""
        # Create directory structure
        base_dir = f"output/{character_id}"
        post_dir = f"{base_dir}/posts"
        media_dir = f"{base_dir}/media"
        for dir_path in [post_dir, media_dir]:
            os.makedirs(dir_path, exist_ok=True)
        
        # Save post metadata and content
        timestamp = post.timestamp.strftime('%Y%m%d_%H%M%S')
        post_file = f"{post_dir}/{timestamp}.txt"
        
        try:
            # Save media files if present
            media_paths = {}
            if hasattr(post, 'image_path') and post.image_path:
                image_path = f"{media_dir}/{timestamp}_image.png"
                os.replace(post.image_path, image_path)
                media_paths['image'] = image_path
                
            if hasattr(post, 'audio_path') and post.audio_path:
                audio_path = f"{media_dir}/{timestamp}_audio.wav"
                os.replace(post.audio_path, audio_path)
                media_paths['audio'] = audio_path
                
            if hasattr(post, 'video_path') and post.video_path:
                video_path = f"{media_dir}/{timestamp}_video.mp4"
                os.replace(post.video_path, video_path)
                media_paths['video'] = video_path
            
            # Update post format with media paths
            post_data = post.to_post_format()
            post_data['media'] = media_paths
            
            # Save post data
            with open(post_file, 'w', encoding='utf-8') as f:
                yaml.dump(post_data, f, allow_unicode=True)
                
            logger.debug(f"Post and media saved to {post_file}")
            
        except Exception as e:
            logger.error(f"Error saving post: {str(e)}")

def main():
    """Main function to run the AI character simulation."""
    parser = argparse.ArgumentParser(description='AI Character Simulation')
    parser.add_argument('--config', default='config/config.yaml', help='Path to config file')
    parser.add_argument('--duration', type=float, default=24.0, help='Simulation duration in hours')
    parser.add_argument('--interval', type=float, default=60.0, help='Post interval in minutes')
    args = parser.parse_args()

    try:
        # Initialize simulation
        simulation = AICharacterSimulation(args.config)
        
        # Create characters
        simulation.create_characters()
        
        # Run simulation for each character
        for character_id in simulation.characters:
            logger.info(f"Starting simulation for character: {character_id}")
            simulation.simulate_character_activity(
                character_id,
                duration_hours=args.duration,
                post_interval_minutes=args.interval
            )
            
    except Exception as e:
        logger.error(f"Simulation failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
