import os
import openai
import logging
import time
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from game import Game  # Ensure Game and LLMClient are in the right path for imports
from client import LLMClient
import http.client

# Set up logger specifically for httpx
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)  # Suppress lower-level logs such as HTTP 200 OK

# Load environment variables from a .env file if it exists
load_dotenv()

# Retrieve API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("API key not found! Please set your OpenAI API key in a .env file or as an environment variable.")

openai.api_key = api_key


def run_parallel_games(num_games, llm_client):
    """
    Runs multiple game instances in parallel using ThreadPoolExecutor.
    Each game is played independently and outputs a session log and summary.
    """
    with ThreadPoolExecutor(max_workers=num_games) as executor:
        futures = [executor.submit(Game(llm_client).play) for _ in range(num_games)]
        
        # Process each game's results as they complete
        for game_count, future in enumerate(as_completed(futures), start=1):
            try:
                session_log, summary = future.result()
                
                # Print session log for each game
                print(f"\n--- Game {game_count} Session Log ---")
                for log_entry in session_log:  # Each question-answer pair
                    print(log_entry)
                
                # Print summary of the game
                print(f"\n--- Game {game_count} Summary ---")
                for key, value in summary.items():
                    print(f"{key}: {value}")
                
            except Exception as e:
                httpx_logger.error(f"Game {game_count} encountered an error: {e}")

#Run Game
if __name__ == "__main__":
    llm_client = LLMClient()
    run_parallel_games(5, llm_client)
