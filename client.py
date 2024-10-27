import os
import openai
from dotenv import load_dotenv
import logging
import time

# Set up logging
logger = logging.getLogger(__name__)
load_dotenv()

class LLMClient:
    def __init__(self, model="gpt-4o-mini"):
        self.model = model
        self.response_times = []

    def generate_response(self, prompt):
        start_time = time.time()
        try:
            # Send prompt to OpenAI's completion endpoint
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            # Calculate and store response time
            response_time = time.time() - start_time
            self.response_times.append(response_time)
            return response.choices[0].message.content.strip()

        except openai.error.OpenAIError as e:
            # Log detailed error
            logger.error(f"OpenAI API Error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None

    def get_response_times(self):
        return self.response_times
