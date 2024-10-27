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
    """Runs a single game session, displaying each question and answer, and makes final guesses if needed."""
    game = Game(llm_client)
    print("\n--- Starting Single Game ---")

    # Initialize game state variables
    asked_questions = []
    wrong_guesses = []
    confirmed_attributes = {}
    contradiction_count = 0
    regeneration_success_count = 0
    question_count = 0
    success = False

    topic = game.host_think_of_topic()
    print("The host has thought of a topic! (secret)")

    # Main question loop, up to 18 turns
    while question_count < 18 and not success:
        question_count += 1
        print(f"\nTurn {question_count}:")  # Print the turn number

        question, contradiction_count, regeneration_success_count = game.guesser.ask_question(
            asked_questions, wrong_guesses, confirmed_attributes, contradiction_count, regeneration_success_count
        )
        print(f"Guesser asks: {question}")

        answer = game.host.answer_question(topic, question)
        print(f"Host answers: {answer}")

        # Update attributes based on the answer
        attribute_key = question.lower().replace("?", "").strip()
        confirmed_attributes[attribute_key] = (answer == "Yes")
        asked_questions.append((question, answer))

        # Win condition check
        if question.lower() in {f"is it an {topic.lower()}?", f"is it a {topic.lower()}?"} and answer.lower() == "yes":
            success = True
            print(f"\nThe guesser wins! The topic was: {topic}")
            break

    # Final guesses if the guesser hasn't won
    if not success:
        print("\nGuesser is now making final guesses...")
        for attempt in range(2):
            guess = game.guesser.reflect_and_guess(asked_questions, wrong_guesses, confirmed_attributes)
            if guess not in wrong_guesses and guess != "Generate another guess.":
                host_response = game.host.evaluate_guess(topic, guess)
                formatted_guess = guess.replace("*", "").replace('"', "").replace(".", "").lower()

                print(f"Guesser's guess: {formatted_guess}\nHost's response: {host_response}")

                if host_response.lower() == "yes":
                    print(f"\nThe guesser wins! The topic was: {topic}")
                    success = True
                    break
                else:
                    wrong_guesses.append(guess)

        if not success:
            print(f"\nThe guesser did not guess the topic correctly. The topic was: {topic}")
            
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
