
import logging
import random
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json
from datetime import datetime
from ..models.character import Character, DailyRoutine, ContentPreferences

logger = logging.getLogger(__name__)

class CharacterGenerator:
    """Generates dynamic AI characters with detailed personalities and routines."""
    
    def __init__(self, mock_mode: bool = False, data_path: Optional[str] = None):
        self.mock_mode = mock_mode
        self._cache = {}
        self._load_character_data(data_path)
        logger.info("Initialized CharacterGenerator")
        
    def _load_character_data(self, data_path: Optional[str] = None) -> None:
        """Load character generation data from file or use defaults."""
        try:
            if data_path and Path(data_path).exists():
                with open(data_path, 'r') as f:
                    data = json.load(f)
                    self.locations = data.get('locations', self._default_locations())
                    self.occupations = data.get('occupations', self._default_occupations())
                    self.interests_by_region = data.get('interests_by_region', self._default_interests())
                logger.info(f"Loaded character data from {data_path}")
            else:
                self.locations = self._default_locations()
                self.occupations = self._default_occupations()
                self.interests_by_region = self._default_interests()
                logger.info("Using default character data")
        except Exception as e:
            logger.error(f"Error loading character data: {str(e)}", exc_info=True)
            raise

    def _default_locations(self) -> Dict[str, List[str]]:
        return {
            'India': ['Mumbai', 'Bangalore', 'Delhi', 'Pune', 'Chennai'],
            'South Korea': ['Seoul', 'Busan', 'Incheon', 'Daegu', 'Daejeon']
        }

    def _default_occupations(self) -> Dict[str, List[str]]:
        return {
            'tech': ['Software Developer', 'UX Designer', 'Data Scientist', 'Game Developer'],
            'creative': ['Content Creator', 'Digital Artist', 'Music Producer', 'Food Blogger'],
            'professional': ['Marketing Specialist', 'Startup Founder', 'Product Manager']
        }

    def _default_interests(self) -> Dict[str, List[str]]:
        return {
            'India': [
                'Classical dance', 'Cricket', 'Bollywood movies', 'Street food',
                'Yoga', 'Tech startups', 'Classical music', 'Photography'
            ],
            'South Korea': [
                'K-pop', 'Gaming', 'Cafe culture', 'Street fashion',
                'Food vlogs', 'Urban photography', 'Electronic music', 'Webtoons'
            ]
        }

    def generate_character(
        self,
        region: str,
        age_range: Tuple[int, int] = (20, 35),
        occupation_category: Optional[str] = None
    ) -> Optional[Character]:
        """Generate a character with specified regional and demographic parameters."""
        if region not in self.locations:
            raise ValueError(f"Unsupported region: {region}")
        if not (isinstance(age_range, tuple) and len(age_range) == 2):
            raise ValueError("Age range must be a tuple of two integers")
        
        try:
            logger.info(f"Generating character for region: {region}")
            
            if self.mock_mode:
                return self._generate_mock_character(region)
            
            # Check cache
            cache_key = f"{region}_{occupation_category}_{age_range}"
            if cache_key in self._cache:
                return self._cache[cache_key]
            
            # Basic demographics
            age = random.randint(age_range[0], age_range[1])
            location = f"{random.choice(self.locations[region])}, {region}"
            
            # Occupation
            if not occupation_category:
                occupation_category = random.choice(list(self.occupations.keys()))
            occupation = random.choice(self.occupations[occupation_category])
            
            # Interests
            base_interests = self.interests_by_region[region]
            occupation_related_interests = self._generate_occupation_interests(occupation)
            interests = random.sample(base_interests, 3) + random.sample(occupation_related_interests, 2)
            
            # Generate other attributes
            personality_traits = self._generate_personality_traits(occupation_category)
            daily_routine = self._generate_daily_routine(occupation, region)
            content_preferences = self._generate_content_preferences(interests, occupation)
            name = self._generate_name(region)
            
            # Create character
            character = Character(
                name=name,
                age=age,
                location=location,
                occupation=occupation,
                interests=interests,
                personality_traits=personality_traits,
                daily_routine=daily_routine,
                content_preferences=content_preferences
            )
            
            # Update cache
            self._cache[cache_key] = character
            
            logger.info(f"Successfully generated character: {name}")
            return character
            
        except Exception as e:
            logger.error(f"Error generating character: {str(e)}", exc_info=True)
            raise

    def _generate_mock_character(self, region: str) -> Character:
        """Generate a simple mock character for testing."""
        return Character(
            name=f"Mock Character ({region})",
            age=25,
            location=f"Mock City, {region}",
            occupation="Mock Occupation",
            interests=["Mock Interest 1", "Mock Interest 2"],
            personality_traits=["Mock Trait 1", "Mock Trait 2"],
            daily_routine=DailyRoutine(
                morning=["Mock morning routine"],
                evening=["Mock evening routine"]
            ),
            content_preferences=ContentPreferences(
                topics=["Mock Topic"],
                formats=["Mock Format"]
            )
        )

    def _generate_name(self, region: str) -> str:
        """Generate region-appropriate name."""
        indian_names = [
            "Aanya Sharma", "Arjun Patel", "Diya Reddy", "Advait Kumar",
            "Zara Menon", "Vihaan Singh", "Ishaan Kapoor", "Anaya Gupta"
        ]
        
        korean_names = [
            "Min-ji Kim", "Jun-ho Park", "Seo-yeon Lee", "Ji-woo Choi",
            "Hae-won Jung", "Tae-hyung Kang", "Yoo-jin Hwang", "Soo-min Yang"
        ]
        
        return random.choice(indian_names if region == 'India' else korean_names)

    def _generate_occupation_interests(self, occupation: str) -> List[str]:
        """Generate occupation-specific interests."""
        interests_map = {
            'Software Developer': [
                'Open source projects', 'AI/ML', 'Hackathons', 'Tech meetups'
            ],
            'Content Creator': [
                'Video editing', 'Social media trends', 'Digital marketing', 'Storytelling'
            ],
            'Game Developer': [
                'Game design', 'Pixel art', 'Game jams', 'Gaming communities'
            ]
        }
        
        return interests_map.get(occupation, ['Professional networking', 'Industry events'])

    def _generate_personality_traits(self, occupation_category: str) -> List[str]:
        """Generate personality traits aligned with occupation."""
        base_traits = [
            'Creative', 'Analytical', 'Ambitious', 'Empathetic',
            'Detail-oriented', 'Innovative', 'Social', 'Introspective'
        ]
        
        occupation_traits = {
            'tech': ['Logical', 'Curious', 'Problem-solver'],
            'creative': ['Expressive', 'Imaginative', 'Free-spirited'],
            'professional': ['Organized', 'Strategic', 'Leadership-oriented']
        }
        
        available_traits = base_traits + occupation_traits.get(occupation_category, [])
        return random.sample(available_traits, 4)

    def _generate_daily_routine(self, occupation: str, region: str) -> DailyRoutine:
        """Generate culturally appropriate daily routine."""
        if region == 'India':
            morning = [
                "6:00 AM: Yoga/Meditation",
                "7:30 AM: Breakfast with family",
                f"9:00 AM: Start {occupation} work"
            ]
            evening = [
                "6:00 PM: Evening activities/hobby",
                "8:00 PM: Family dinner",
                "10:00 PM: Content creation/relaxation"
            ]
        else:  # South Korea
            morning = [
                "7:00 AM: Morning exercise",
                "8:30 AM: Breakfast at local cafe",
                f"9:30 AM: Start {occupation} work"
            ]
            evening = [
                "6:30 PM: After-work hobby activities",
                "8:30 PM: Personal projects",
                "11:00 PM: Late night content creation"
            ]
        
        return DailyRoutine(morning=morning, evening=evening)

    def _generate_content_preferences(self, interests: List[str], occupation: str) -> ContentPreferences:
        """Generate content preferences based on interests and occupation."""
        # Base topics from interests
        topics = [f"{interest.lower()} tips" for interest in interests]
        
        # Add occupation-specific topics
        occupation_topics = {
            'Software Developer': ['Technology tutorials', 'Coding tips'],
            'Content Creator': ['Content strategy', 'Creative process'],
            'Game Developer': ['Game development', 'Gaming industry insights']
        }
        topics.extend(occupation_topics.get(occupation, [f"{occupation.lower()} insights"]))
        
        formats = [
            "Tutorial videos",
            "Day-in-life vlogs",
            "Behind-the-scenes",
            "Quick tips",
            "Story time",
            "Project showcases"
        ]
        
        return ContentPreferences(
            topics=random.sample(topics, min(4, len(topics))),
            formats=random.sample(formats, 4)
        )

    def clear_cache(self) -> None:
        """Clear the character generation cache."""
        self._cache.clear()
        logger.info("Character generation cache cleared")