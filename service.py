import os
# pyrefly: ignore [missing-import]
from google import genai
# pyrefly: ignore [missing-import]
from google.genai import types
from models import Message

class GeminiService:
    def __init__(self):
        self.client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        self.model = os.environ["GEMINI_MODEL"]

    def send(self, history: list[Message]) -> str:
        contents = [
            types.Content(role=m.role, parts=[types.Part(text=m.text)])
            for m in history
        ]
        response = self.client.models.generate_content(model=self.model, contents=contents)
        return response.text