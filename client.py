import os
import openai
from dotenv import load_dotenv
import logging
import time  # If you're tracking response times

class LLMClient:
    """
    LLMClient handles interactions with the OpenAI API, including logging response times 
    for performance tracking. This class uses the model specified during initialization.
    """
    def __init__(self, model="gpt-4"):
        self.model = model
        self.response_times = []

    def generate_response(self, prompt):
        """
        Generates a response from the OpenAI API for the given prompt.
        Measures response time and logs any errors encountered.
        """
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
        except Exception as e:
            # Log error in case of failure
            logger.error(f"Error generating response: {e}")
            return None

    def get_response_times(self):
        """Returns the list of response times for performance evaluation."""
        return self.response_times

