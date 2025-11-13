import requests
import json
import os
from django.conf import settings

class OpenRouterService:
    def __init__(self):
        # Read API key from environment variable
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is not set. "
                "Please add it to your .env file."
            )
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "meta-llama/llama-3.3-70b-instruct:free"
    
    def generate_explanation(self, user_context, movie_context):
        """Generate a natural language explanation for why a movie is recommended"""
        
        # Create context-aware prompt
        prompt = f"""
        You are a helpful movie recommendation assistant. Based on the user's movie preferences, explain why they might enjoy this specific movie.
        
        User's rating history and preferences:
        {user_context}
        
        Movie information:
        {movie_context}
        
        Provide a complete, natural explanation of why this movie would appeal to this user, framed in exactly 40 words. Be conversational and personal, as if you know their taste well, focusing on patterns in their ratings and what makes this movie a good match.
        """
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://moviewise-xai.com",
            "X-Title": "MovieWise XAI"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a movie recommendation expert who creates natural, personalized explanations for why users might enjoy specific movies. Your explanation must be exactly 40 words and be a complete, coherent response without any abrupt breaks, ending gracefully."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 60, # Adjusted max_tokens to encourage exactly 40 words
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                explanation = data['choices'][0]['message']['content'].strip()
                
                # Post-process to strictly enforce 40-word count
                words = explanation.split()
                if len(words) > 40:
                    explanation = " ".join(words[:40]) + "..."
                elif len(words) < 40:
                    # If it's too short, we can't force it to be 40 without fabrication.
                    # We'll just ensure it ends gracefully.
                    pass
                
                # Ensure it ends with punctuation if truncated or doesn't naturally
                if not explanation.endswith(('.', '!', '?')) and not explanation.endswith("..."):
                    explanation += "."
                    
                return explanation
            else:
                print(f"OpenRouter API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"OpenRouter API exception: {str(e)}")
            return None

# Global instance
openrouter_service = OpenRouterService()