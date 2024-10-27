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

class LLMClient:
    def __init__(self, model="gpt-4o-mini", temperature=0.3):  
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.temperature = temperature  
        self.response_times = []
        
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set it in the .env file.")

    def generate_response(self, prompt, temperature=None):
        # Use passed temperature or fall back to the default temperature
        temperature = temperature if temperature is not None else self.temperature
        start_time = time.time()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature  
        }
        try:
            # Setting a custom timeout
            with httpx.Client(timeout=10) as client:
                response = client.post("https://api.openai.com/v1/chat/completions", json=data, headers=headers)
                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"].strip()
                
                # Log response time (set to DEBUG to suppress if needed)
                response_time = time.time() - start_time
                self.response_times.append(response_time)
                
                return content
        except httpx.TimeoutException:
            httpx_logger.error("Request timed out. Skipping this prompt.")
            return None
        except httpx.HTTPStatusError as e:
            httpx_logger.error(f"HTTP error occurred: {e}")
            return None
        except Exception as e:
            httpx_logger.error(f"Unexpected error: {e}")
            return None

    def get_response_times(self):
        return self.response_times
