class Game:
    """
    The Game class manages a single game session, handling the interaction 
    between the Host and the Guesser.
    """
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.host = Host(llm_client)
        self.guesser = Guesser(llm_client)
        self.asked_questions = []
        self.wrong_guesses = []
        self.question_count = 0
        self.success = False
        self.regeneration_count = 0  # Local regeneration counter for this game instance

    def play(self):
        """
        Conducts the question-and-answer session between the Guesser and the Host.
        Ends either when the Guesser wins or the question limit is reached.
        """
        session_log = []
        self.question_count = 0
        self.success = False
        while self.question_count < 18 and not self.success:
            self.question_count += 1
            question, self.regeneration_count = self.guesser.ask_question(self.asked_questions, self.regeneration_count)
            answer = self.host.answer_question(question, self.asked_questions)
            session_log.append(f"Question {self.question_count}: {question} - Answer: {answer}")
            self.asked_questions.append((question, answer))
            
            # Check for a direct guess if it matches the topic
            if question.lower() in {f"is it an {self.host.topic.lower()}?", f"is it a {self.host.topic.lower()}?"}:
                self.success = True
                break

        # If no success, enter final guessing phase
        if not self.success:
            self.final_guesses(session_log)
        
        return session_log, self.evaluation_summary()

    def final_guesses(self, session_log):
        """Allows the Guesser to make final guesses if the topic isn't identified within 18 questions."""
        session_log.append("Entering final guess phase...")
        for _ in range(2):
            guess = self.guesser.reflect_and_guess(self.asked_questions, self.wrong_guesses)
            host_response = self.host.evaluate_guess(guess)
            session_log.append(f"Final Guess: {guess} - Host's response: {host_response}")
            if self.host.topic.strip(".").lower() == guess.strip().lower():
                self.success = True
                session_log.append(f"The guesser wins! The topic was: {self.host.topic}")
                break
            else:
                self.wrong_guesses.append(guess)

        # Record unsuccessful ending if applicable
        if not self.success:
            session_log.append(f"The guesser did not guess the topic correctly. The topic was: {self.host.topic}")

    def evaluation_summary(self):
        """
        Summarises game metrics such as total questions asked, regeneration count, 
        and average response time.
        """
        total_time = sum(self.llm_client.get_response_times())
        average_response_time = total_time / len(self.llm_client.get_response_times()) if self.llm_client.get_response_times() else 0
        return {
            "Total Questions Asked": self.question_count,
            "Total Regenerations for this Game": self.regeneration_count,
            "Total Response Time": total_time,
            "Average Response Time per Question": average_response_time
        }
