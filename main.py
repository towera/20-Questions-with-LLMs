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
    """Runs a single instance of the game, displaying each question and response immediately, and shows summary at the end."""
    game = Game(llm_client)
    question_count = 0
    success = False

    print("\n--- Single Game Start ---")
    while question_count < 18 and not success:
        question_count += 1
        print(f"\nTurn {question_count}:")  # Display turn number

        # Get question and answer for the current turn
        question, regeneration_count = game.guesser.ask_question(game.asked_questions, game.regeneration_count)
        answer = game.host.answer_question(question, game.asked_questions)

        # Print the question and answer
        print(f"Guesser asks: {question}")
        print(f"Host answers: {answer}")

        # Track asked questions and answers
        game.asked_questions.append((question, answer))

        # Check if guesser has guessed the topic directly
        if answer.lower() == "yes" and question.lower() in {f"is it an {game.host.topic.lower()}?", f"is it a {game.host.topic.lower()}?"}:
            print(f"\nThe guesser wins! The topic was: {game.host.topic}")
            success = True  # Set success to True if guesser wins
            break

    # Final guesses if the topic was not guessed in 18 questions
    if not success:
        print("\nGuesser is now making final guesses...")
        for attempt in range(2):
            guess = game.guesser.reflect_and_guess(game.asked_questions, game.wrong_guesses)
            if guess not in game.wrong_guesses and guess != "Generate another guess.":
                host_response = game.host.evaluate_guess(guess)
                print(f"Guesser's guess: {guess}\nHost's response: {host_response}")

                if host_response.lower() == "yes":
                    print(f"\nThe guesser wins! The topic was: {game.host.topic}")
                    success = True
                    break
                else:
                    game.wrong_guesses.append(guess)

        if not success:
            print(f"\nThe guesser did not guess the topic correctly. The topic was: {game.host.topic}")

    # Print game summary
    summary = game.evaluation_summary()
    print("\n--- Single Game Summary ---")
    for key, value in summary.items():
        print(f"{key}: {value}")



def run_parallel_games(num_games, llm_client):
    """
    Runs multiple game instances in parallel using ThreadPoolExecutor.
    Each game is played independently and outputs a session log and summary.
    """
    with ThreadPoolExecutor(max_workers=num_games) as executor:
        futures = []
        
        for i in range(num_games):
            print(f"Running game {i + 1} of {num_games}...")  # Print status for each game start
            futures.append(executor.submit(Game(llm_client).play))
        
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
    
    while True:
        choice = input("Enter '1' to run a single game or '2' to run multiple games in parallel: ").strip()
        
        if choice == '1':
            run_single_game(llm_client)
            break  # Exit after running single game
        elif choice == '2':
            try:
                num_games = int(input("Enter the number of games to run in parallel: ").strip())
                if num_games > 0:
                    run_parallel_games(num_games, llm_client)
                    break  # Exit after running parallel games
                else:
                    print("Please enter a positive integer for the number of games.")
            except ValueError:
                print("Invalid input. Please enter a valid integer.")
        else:
            print("Invalid choice. Please enter '1' or '2'.")

