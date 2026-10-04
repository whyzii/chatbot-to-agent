import os
# pyrefly: ignore [missing-import]
from groq import Groq
from models import Message

class GroqService:
    def __init__(self):
        self.client = Groq(api_key=os.environ["GROQ_API_KEY"])
        self.model = os.environ["GROQ_MODEL"]

    def send(self, history: list[Message], system_prompt: str | None = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages += [
            {"role": "assistant" if m.role == "model" else "user", "content": m.text}
            for m in history
        ]
        response = self.client.chat.completions.create(model=self.model, messages=messages)
        return response.choices[0].message.content