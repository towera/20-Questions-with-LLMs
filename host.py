import logging
from client import LLMClient  # Assumes client.py and LLMClient are in the same directory

class Host:
    """
    The Host class selects a topic and manages responses to questions from the Guesser.
    It uses LLMClient to generate a random topic and determine its characteristics.
    """
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.topic, self.characteristics = self.think_of_topic()

    def think_of_topic(self):
        """
        Selects a random topic and retrieves its main characteristics 
        by prompting the LLM.
        """
        # Higher temperature for topic generation to increase variety
        topic_prompt = "Think of one random living or non-living thing. Only respond with the name of the object or living thing."
        topic = self.llm_client.generate_response(topic_prompt, temperature=0.8) or "unknown"
        
        # Higher temperature for characteristic generation to add more diverse attributes
        characteristic_prompt = (
            f"You chose '{topic}'. List key characteristics like if it is living, an animal, plant, "
            "edible, fruit, etc. Only provide characteristics in a list format."
        )
        characteristics = self.llm_client.generate_response(characteristic_prompt, temperature=0.7) or "N/A"
        
        return topic, characteristics

    def answer_question(self, question, asked_questions):
        """
        Processes each question from the Guesser and provides an answer 
        based on the topic's characteristics.
        """
        reflection = f"The topic is '{self.topic}', with characteristics: {self.characteristics}. Think of other characteristics of the {self.topic}. The question asked is: '{question}'."
        previous_context = f"Previous questions and answers: {asked_questions}."
        cot_reasoning = (
            "Step 1: Based on topic characteristics, determine if the question aligns with its attributes. "
            "Step 2: Ensure consistency with previous answers. Step 3: Provide an accurate Yes or No response."
        )
        action = "Given this, answer 'Yes' or 'No' as accurately as possible."
        
        prompt = f"{reflection}\n\n{previous_context}\n\n{cot_reasoning}\n\n{action}"
        answer = self.llm_client.generate_response(prompt).strip()
        
        if "yes" in answer.lower():
            return "Yes"
        elif "no" in answer.lower():
            return "No"
        else:
            return "Invalid answer"
  
    def evaluate_guess(self, guess):
        """Evaluates the Guesser's guess against the chosen topic."""
        return "Yes" if self.topic.strip(".").lower() == guess.strip().lower() else "No"
