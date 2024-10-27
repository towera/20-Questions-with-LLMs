import os
import openai
import logging
import time
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from game import Game  # Ensure Game and LLMClient are in the right path for imports
from client import LLMClient
import http.client

http.client.HTTPConnection.debuglevel = 0

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logging.getLogger("requests").setLevel(logging.ERROR)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)
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
        
        # Loop over completed futures
        for game_count, future in enumerate(as_completed(futures), start=1):
            session_log, summary = future.result()
            print(f"\n--- Game {game_count} Session Log ---")
            
            # Print the evaluation summary for each game directly
            print(f"\n--- Game {game_count} Summary ---")
            for key, value in summary.items():
                print(f"{key}: {value}")


# Example usage
if __name__ == "__main__":
    llm_client = LLMClient()
    run_parallel_games(5, llm_client)
