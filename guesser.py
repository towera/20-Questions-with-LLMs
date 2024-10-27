class Guesser:
    """
    The Guesser class formulates yes/no questions to narrow down the topic.
    It avoids repeating questions by maintaining a record of asked attributes.
    """
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.asked_attributes = set()

    def ask_question(self, asked_questions, regeneration_count):
        """
        Generates a new question for the Host, ensuring it hasn't been asked before.
        If a redundant question is generated, it increments the regeneration counter.
        """
        # Update asked attributes based on previously asked questions
        self.update_asked_attributes(asked_questions)
        
        while True:  # Loop until a valid, unique question is generated
            reflection = f"These are the questions asked so far and their answers: {asked_questions}."
            cot_reasoning = (
                "Step 1: Identify if the topic is a living or non-living entity. "
                "Step 2: Based on the identified category, ask questions about common distinguishing characteristics. "
                "Step 3: Avoid repeating information or switching to unrelated categories once a category is confirmed."
            )
            action = "Based on the current confirmed characteristics and answers, what is the next logical yes/no question that will help further narrow down the topic, staying within broader categories before refining?"
            prompt = f"{reflection}\n\n{cot_reasoning}\n\n{action}"
            
            response = self.llm_client.generate_response(prompt).strip()
            
            # Extract question from response and validate uniqueness
            match = re.search(r'"([^"]+)"', response)
            if match:
                question = match.group(1)
                if question not in self.asked_attributes:
                    self.asked_attributes.add(question)
                    return question, regeneration_count  # Return the new, unique question
                else:
                    regeneration_count += 1
                    logger.info("Regenerating due to redundant question.")
            else:
                regeneration_count += 1
                logger.info("Regenerating due to invalid question format.")

    def update_asked_attributes(self, asked_questions):
        """Updates the list of asked attributes to avoid redundancy."""
        for question, _ in asked_questions:
            self.asked_attributes.add(question.lower())
  
    def reflect_and_guess(self, asked_questions, wrong_guesses):
        """
        Reflects on the game history and makes a final guess.
        It avoids guesses that have already been proven incorrect.
        """
        reflection = f"These are the questions and answers so far: {asked_questions}. These are the wrong guesses: {wrong_guesses}."
        cot_reasoning = (
            "Step 1: Focus on 'Yes' responses for clues. Step 2: Use 'No' responses to eliminate possibilities."
        )
        action = "Return only the one- or two-word item that is the most logical guess."
        
        prompt = f"{reflection}\n\n{cot_reasoning}\n\n{action}"
        guess = self.llm_client.generate_response(prompt).strip()
        
        if guess in wrong_guesses:
            return "Generate another guess."
        return guess

