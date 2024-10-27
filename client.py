import os
import logging
import httpx
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging for httpx to suppress HTTP 200 logs
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, model="gpt-4o-mini"):
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.response_times = []
        
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set it in the .env file.")

    def generate_response(self, prompt):
        start_time = time.time()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }
        try:
            with httpx.Client() as client:
                response = client.post("https://api.openai.com/v1/chat/completions", json=data, headers=headers)
                response.raise_for_status()  # Raise an error for non-200 responses
                content = response.json()["choices"][0]["message"]["content"].strip()
                
                # Calculate and store response time
                response_time = time.time() - start_time
                self.response_times.append(response_time)
                
                return content
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None

    def get_response_times(self):
        return self.response_times
