from dataclasses import dataclass

@dataclass
class Message:
    role: str   # "user" or "model" (Gemini's word for the bot)
    text: str