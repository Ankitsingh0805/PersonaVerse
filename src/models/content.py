from dataclasses import dataclass
from typing import List, Dict
import random
from datetime import datetime, time

@dataclass
class Content:
    character_name: str
    timestamp: datetime
    content_type: str  # text, image, video, audio
    content: str
    mood: str
    context: str
    metadata: Dict[str, str]
    hashtags: List[str]

    def to_post_format(self) -> Dict[str, any]:
        """Converts content to a social media post format."""
        return {
            "author": self.character_name,
            "timestamp": self.timestamp.isoformat(),
            "content": self.content,
            "mood": self.mood,
            "hashtags": self.hashtags,
            "metadata": {
                **self.metadata,
                "generation_context": self.context,
                "content_type": self.content_type
            }
        }

    @staticmethod
    def generate_hashtags(context: Dict[str, str], location: str) -> List[str]:
        """Generates relevant hashtags based on content context."""
        def clean_text(text: str) -> str:
            return ''.join(c for c in text.title() if c.isalnum())

        # Location-based hashtags
        location_parts = location.split(',')
        city = clean_text(location_parts[0].strip())
        country = clean_text(location_parts[-1].strip())
        
        # Base hashtags
        base_hashtags = [
            f"#{city}Life",
            f"#{country}Life",
            f"#{clean_text(context['topic'])}",
            f"#{clean_text(context['format'])}"
        ]

        # Mood and activity hashtags
        mood_hashtag = f"#{clean_text(context['mood'])}"
        activity_hashtag = f"#{clean_text(context['context'])}"

        # Additional contextual hashtags
        time_of_day = datetime.now().strftime("%p").lower()
        time_hashtag = f"#{time_of_day}{city}"

        return list(set(base_hashtags + [mood_hashtag, activity_hashtag, time_hashtag]))