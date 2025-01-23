from main import AICharacterSimulation
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def run_simple_simulation():
    """Run a short simulation with frequent posts"""
    try:
        simulation = AICharacterSimulation()
        simulation.create_characters()
        
        # Display character info
        for char_id, character in simulation.characters.items():
            print(f"\n{'='*50}")
            print(f"Character: {character.name}")
            print(f"Location: {character.location}")
            print(f"Age: {character.age}")
            print(f"Occupation: {character.occupation}")
            print(f"Personality: {', '.join(character.personality_traits)}")
            print(f"Interests: {', '.join(character.interests)}")
            print(f"Current Activity: {character.get_current_activity()}")
        
        # Run short simulation
        for char_id in simulation.characters:
            simulation.simulate_character_activity(
                char_id,
                duration_hours=0.1,    # 30 minutes
                post_interval_minutes=0.3 # Post every 5 minutes
            )
            
    except Exception as e:
        print(f"Simulation error: {str(e)}")
        raise

if __name__ == "__main__":
    run_simple_simulation()