from dataclasses import dataclass
from typing import List, Dict
import random
from datetime import datetime, time

@dataclass
class DailyRoutine:
    morning: List[str]
    evening: List[str]

@dataclass
class ContentPreferences:
    topics: List[str]
    formats: List[str]

@dataclass
class Character:
    name: str
    age: int
    location: str
    occupation: str
    interests: List[str]
    personality_traits: List[str]
    daily_routine: DailyRoutine
    content_preferences: ContentPreferences

    def get_current_activity(self) -> str:
        """Determines character's current activity based on their daily routine and time."""
        current_time = datetime.now().time()

        def parse_time(time_str: str) -> time:
            try:
                return datetime.strptime(time_str.split(':')[0], '%H').time()
            except ValueError as e:
                # Fallback to default activity if time parsing fails
                return current_time

        # Check morning activities
        for activity in self.daily_routine.morning:
            if ': ' not in activity:
                continue
            activity_time = parse_time(activity.split(': ')[0])
            if current_time >= activity_time:
                return activity.split(': ')[1]

        # Check evening activities    
        for activity in self.daily_routine.evening:
            if ': ' not in activity:
                continue
            activity_time = parse_time(activity.split(': ')[0])
            if current_time >= activity_time:
                return activity.split(': ')[1]

        return "Free time"

    def generate_mood(self) -> str:
        """Generates a realistic mood based on time and personality traits."""
        current_hour = datetime.now().hour
        
        # Base energy level influenced by personality
        base_energy = 0.7
        if 'Energetic' in self.personality_traits:
            base_energy += 0.1
        if 'Introspective' in self.personality_traits:
            base_energy -= 0.1
            
        energy_level = random.gauss(base_energy, 0.2)  # Normal distribution
        
        # Time-based adjustments
        time_multipliers = {
            (0, 6): 0.5,    # Late night/early morning
            (6, 11): 1.2,   # Morning
            (11, 15): 0.9,  # Early afternoon
            (15, 20): 1.1,  # Late afternoon/evening
            (20, 24): 0.8   # Night
        }
        
        for (start, end), multiplier in time_multipliers.items():
            if start <= current_hour < end:
                energy_level *= multiplier
                break

        # Personality-influenced moods
        moods = {
            (0.8, 1.0): {
                'Creative': ["inspired", "innovative", "imaginative"],
                'Analytical': ["focused", "determined", "engaged"],
                'default': ["excited", "energetic", "enthusiastic"]
            },
            (0.6, 0.8): {
                'Social': ["friendly", "sociable", "connected"],
                'Professional': ["productive", "efficient", "focused"],
                'default': ["content", "positive", "balanced"]
            },
            (0.4, 0.6): {
                'Introspective': ["contemplative", "thoughtful", "meditative"],
                'Empathetic': ["caring", "understanding", "compassionate"],
                'default': ["calm", "neutral", "steady"]
            },
            (0.2, 0.4): {
                'Detail-oriented': ["careful", "precise", "methodical"],
                'Innovative': ["brainstorming", "exploring", "curious"],
                'default': ["tired", "quiet", "reserved"]
            },
            (0.0, 0.2): {
                'Ambitious': ["determined", "persevering", "pushing_through"],
                'default': ["exhausted", "need_rest", "reflective"]
            }
        }

        # Find appropriate mood range
        for (lower, upper), mood_categories in moods.items():
            if lower <= energy_level <= upper:
                # Check personality traits for specific moods
                for trait, trait_moods in mood_categories.items():
                    if trait in self.personality_traits:
                        return random.choice(trait_moods)
                return random.choice(mood_categories['default'])

        return "neutral"

    def get_content_idea(self) -> Dict[str, str]:
        """Generates a content idea based on current context and preferences."""
        current_activity = self.get_current_activity()
        mood = self.generate_mood()
        
        # Weight topics based on current context and interests
        weighted_topics = []
        for topic in self.content_preferences.topics:
            weight = 1.0
            # Increase weight if topic relates to current activity
            if any(word in current_activity.lower() for word in topic.lower().split()):
                weight += 0.5
            # Increase weight if topic relates to interests
            if any(interest in topic.lower() for interest in self.interests):
                weight += 0.3
            weighted_topics.append((topic, weight))
        
        # Select topic based on weights
        total_weight = sum(w for _, w in weighted_topics)
        r = random.uniform(0, total_weight)
        current_weight = 0
        for topic, weight in weighted_topics:
            current_weight += weight
            if current_weight >= r:
                selected_topic = topic
                break
        else:
            selected_topic = random.choice(self.content_preferences.topics)

        # Select appropriate format based on mood and activity
        format_weights = {}
        for format_ in self.content_preferences.formats:
            weight = 1.0
            # Adjust weights based on mood
            if mood in ["tired", "exhausted"] and format_ in ["Tutorial videos", "Long-form content"]:
                weight -= 0.3
            elif mood in ["energetic", "inspired"] and format_ in ["Quick tips", "Behind-the-scenes"]:
                weight += 0.3
            format_weights[format_] = weight
        
        format_ = random.choices(
            list(format_weights.keys()),
            weights=list(format_weights.values())
        )[0]

        return {
            "topic": selected_topic,
            "format": format_,
            "mood": mood,
            "context": current_activity
        }