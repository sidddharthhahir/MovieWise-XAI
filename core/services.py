import logging
import os

import requests


logger = logging.getLogger(__name__)

class OllamaService:
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2")
    
    def generate_explanation(self, user_context, movie_context):
        """Generate a natural language explanation using local Ollama LLM."""
        prompt = f"""You are a helpful movie recommendation assistant. Based on the user's movie preferences, explain why they might enjoy this specific movie.

User's rating history and preferences:
{user_context}

Movie information:
{movie_context}

Provide a complete, natural explanation of why this movie would appeal to this user in exactly 40 words. Be conversational and personal, as if you know their taste well, focusing on patterns in their ratings and what makes this movie a good match. End with proper punctuation."""
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 80  # Max tokens to generate
            }
        }
        
        try:
            logger.debug("Calling Ollama API at %s/api/generate with model %s", self.base_url, self.model)
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60  # Ollama can be slower on first run
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'response' not in data:
                    logger.warning("Unexpected Ollama response structure")
                    return None

                explanation = data['response'].strip()
                words = explanation.split()
                if len(words) > 45:
                    explanation = " ".join(words[:40])
                    if '.' in explanation:
                        last_period = explanation.rfind('.')
                        if last_period > len(explanation) * 0.7:
                            explanation = explanation[:last_period + 1]
                    else:
                        explanation += "..."

                if not explanation.endswith(('.', '!', '?', '...')):
                    explanation += "."

                return explanation

            logger.warning("Ollama API returned status %s", response.status_code)
            return None

        except requests.exceptions.Timeout:
            logger.warning("Ollama API timeout after 60 seconds")
            return None
        except requests.exceptions.ConnectionError as e:
            logger.warning("Ollama connection error: %s", e)
            return None
        except Exception:
            logger.exception("Unhandled Ollama API error")
            return None

openrouter_service = OllamaService()