import requests
import json
import os

class OllamaService:
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.model = "llama3.2"  # Change to "phi3.5" or "mistral" if you downloaded those
    
    def generate_explanation(self, user_context, movie_context):
        """Generate a natural language explanation using local Ollama LLM"""
        
        # Create context-aware prompt
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
            print(f"🔍 Calling local Ollama LLM...")
            print(f"🌐 Ollama URL: {self.base_url}/api/generate")
            print(f"🤖 Model: {self.model}")
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60  # Ollama can be slower on first run
            )
            
            print(f"📡 Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Ollama returns response in "response" field
                if 'response' not in data:
                    print(f"⚠️ Unexpected response structure: {data}")
                    return None
                
                explanation = data['response'].strip()
                print(f"✅ LLM raw response: {explanation[:200]}...")
                
                # Post-process to enforce ~40-word count
                words = explanation.split()
                if len(words) > 45:
                    # Truncate to 40 words
                    explanation = " ".join(words[:40])
                    # Try to end at a sentence boundary
                    if '.' in explanation:
                        last_period = explanation.rfind('.')
                        if last_period > len(explanation) * 0.7:
                            explanation = explanation[:last_period + 1]
                    else:
                        explanation += "..."
                
                # Ensure it ends with punctuation
                if not explanation.endswith(('.', '!', '?', '...')):
                    explanation += "."
                
                word_count = len(explanation.split())
                print(f"✅ Final explanation ({word_count} words): {explanation}")
                return explanation
                
            else:
                error_text = response.text
                print(f"❌ Ollama API error: {response.status_code}")
                print(f"❌ Error details: {error_text}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"❌ Ollama API timeout after 60 seconds")
            print(f"💡 Tip: First run can be slow. Make sure 'ollama serve' is running.")
            return None
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Ollama connection error: {str(e)}")
            print(f"💡 Make sure Ollama is running: 'ollama serve'")
            return None
        except Exception as e:
            print(f"❌ Ollama API exception: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

# Global instance - using Ollama instead of OpenRouter
openrouter_service = OllamaService()  # Keep same name so views.py doesn't need changes