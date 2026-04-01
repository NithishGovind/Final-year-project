import requests


class LLMFeedback:

    def __init__(self, model="llama3.2:1b"):
        self.model = model
        self.url = "http://localhost:11434/api/generate"

    def generate_feedback(self, analysis_data):

        prompt = f"""
You are a strict chess coach.

White is the human.
Black is the engine.

Position (FEN): {analysis_data['fen']}
White played: {analysis_data['played_move']}
Evaluation change: {analysis_data['evaluation_change']} pawns.

If evaluation change < -1 → call it a mistake.
If evaluation change < -2 → call it a blunder.
If evaluation change > 1 → call it strong.

Respond in ONE short sentence if the move is good, if it is a blunder explain the correct move shortly and do not talk about any evaluation number metrics, please be human as possible.
"""

        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
        )

        return response.json()["response"]