from models import Message
from service import GeminiService

class ChatViewModel:
    def __init__(self, service: GeminiService):
        self.service = service
        self.messages: list[Message] = []

    def send(self, text: str) -> str:
        self.messages.append(Message(role="user", text=text))
        try:
            reply = self.service.send(self.messages)
        except Exception:
            self.messages.pop()
            raise
        self.messages.append(Message(role="model", text=reply))
        return reply