import os
import openai
import logging
import time
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from game import Game  # Ensure Game and LLMClient are in the correct path for imports
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


def run_single_game(llm_client):
    """Runs a single instance of the game and outputs the session log and summary."""
    game = Game(llm_client)
    print("\n--- Starting Single Game ---")
    session_log, summary = game.play()
    
    # Print each question and response as they occur
    for question, response in session_log:
        print(f"Question: {question} - Host's response: {response}")
    
    # Check the winning condition after the game completes
    if summary["win"]:
        print(f"\nThe guesser wins! The topic was: {summary['topic']}")
    else:
        print(f"\nThe guesser did not guess the topic correctly. The topic was: {summary['topic']}")

    # Print summary of the game
    print("\n--- Single Game Summary ---")
    for key, value in summary.items():
        print(f"{key}: {value}")


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
                for log_entry in session_log:
                    print(log_entry)
                
                # Print summary of the game
                print(f"\n--- Game {game_count} Summary ---")
                for key, value in summary.items():
                    print(f"{key}: {value}")
                
            except Exception as e:
                httpx_logger.error(f"Game {game_count} encountered an error: {e}")

# Prompt user to decide between single or parallel games
if __name__ == "__main__":
    llm_client = LLMClient()
    
    choice = input("Enter '1' to run a single game or '2' to run multiple games in parallel: ").strip()
    
    if choice == '1':
        run_single_game(llm_client)
    elif choice == '2':
        try:
            num_games = int(input("Enter the number of games to run in parallel: ").strip())
            if num_games > 0:
                run_parallel_games(num_games, llm_client)
            else:
                print("Please enter a positive integer for the number of games.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")
    else:
        print("Invalid choice. Please enter '1' or '2'.")
