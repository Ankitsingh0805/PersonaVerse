
import logging
from typing import List, Dict, Optional
import torch
from transformers import PreTrainedModel, PreTrainedTokenizer
import random
from collections import deque

logger = logging.getLogger(__name__)

class TextGenerator:
    """Advanced text generation utility for AI characters."""
    
    def __init__(
        self,
        model: PreTrainedModel,
        tokenizer: PreTrainedTokenizer,
        mock_mode: bool = False,
        max_history: int = 10
    ):
        self.mock_mode = mock_mode
        self.model = model
        self.tokenizer = tokenizer
        self.max_history = max_history
        self.conversation_history = deque(maxlen=max_history)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.templates = {
            'excited': [
                "Can't wait to share this! {content}",
                "You won't believe what happened! {content}",
                "I'm so thrilled about this! {content}"
            ],
            'thoughtful': [
                "Been thinking about this lately... {content}",
                "Here's my perspective: {content}",
                "After careful consideration: {content}"
            ],
            'creative': [
                "Just had a creative burst! {content}",
                "Here's something I came up with: {content}",
                "Experimenting with this idea: {content}"
            ]
        }
        
        self.vocab_enhancers = {
            'tech': ['innovation', 'development', 'algorithm', 'interface', 'system'],
            'food': ['flavors', 'aroma', 'texture', 'cuisine', 'ingredients'],
            'culture': ['tradition', 'heritage', 'celebration', 'community', 'festival']
        }
        
        logger.info(f"Initialized TextGenerator with device: {self.device}")

    @torch.no_grad()
    def generate_with_style(
        self,
        prompt: str,
        character_traits: List[str],
        mood: str,
        topic: str,
        max_length: int = 2000,
        temperature: float = 0.7
    ) -> Optional[str]:
        """Generate text with character-specific style and context."""
        if not prompt or not character_traits or not mood or not topic:
            raise ValueError("All parameters must be provided")
        
        try:
            logger.info(f"Generating text for mood: {mood}, topic: {topic}")
            
            if self.mock_mode:
                return f"Mock generated text for {topic}"
            
            
            enhanced_prompt = self._enhance_prompt(prompt, character_traits, topic)
            
            # Generate text
            inputs = self.tokenizer(enhanced_prompt, return_tensors="pt", padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                do_sample=True,
                temperature=temperature,
                top_p=0.9,
                top_k=50,
                no_repeat_ngram_size=2,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
            
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Apply mood-based formatting
            formatted_text = self._format_with_mood(generated_text, mood)
            
            # Update conversation history
            self.conversation_history.append(formatted_text)
            
            logger.info("Successfully generated text")
            return formatted_text
            
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}", exc_info=True)
            raise

    def _enhance_prompt(self, prompt: str, character_traits: List[str], topic: str) -> str:
        """Enhance prompt with character traits and topic-specific vocabulary."""
        try:
            trait_phrases = [f"Speaking as someone who is {trait}" for trait in character_traits]
            topic_words = self.vocab_enhancers.get(topic.lower(), [])
            
            enhanced_prompt = f"{', '.join(trait_phrases)}. {prompt}"
            if topic_words:
                enhanced_prompt += f" Consider these relevant terms: {', '.join(topic_words)}"
            
            logger.debug(f"Enhanced prompt: {enhanced_prompt}")
            return enhanced_prompt
            
        except Exception as e:
            logger.error(f"Error enhancing prompt: {str(e)}", exc_info=True)
            raise

    def _format_with_mood(self, text: str, mood: str) -> str:
        """Format text based on character's current mood."""
        try:
            templates = self.templates.get(mood.lower(), ["{content}"])
            template = random.choice(templates)
            
            text = text.strip()
            if text.startswith('"') and text.endswith('"'):
                text = text[1:-1]
            
            formatted_text = template.format(content=text)
            return formatted_text
            
        except Exception as e:
            logger.error(f"Error formatting with mood: {str(e)}", exc_info=True)
            raise

    def get_context_aware_response(
        self,
        prompt: str,
        context: Dict[str, any]
    ) -> Optional[str]:
        """Generate response considering recent conversation history and context."""
        try:
            # Include recent history for context
            history_text = "\n".join(list(self.conversation_history)[-3:])
            context_prompt = f"{history_text}\n{prompt}" if history_text else prompt
            
            return self.generate_with_style(
                prompt=context_prompt,
                character_traits=context.get('character_traits', []),
                mood=context.get('mood', 'neutral'),
                topic=context.get('topic', 'general')
            )
            
        except Exception as e:
            logger.error(f"Error generating context-aware response: {str(e)}", exc_info=True)
            raise

    def __del__(self):
        """Cleanup resources."""
        try:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            logger.info("Cleaned up TextGenerator resources")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")