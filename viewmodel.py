from models import Message
from storage import ChatStorage

class ChatViewModel:
    def __init__(self, service, storage: ChatStorage):
        self.service = service
        self.storage = storage
        self.messages: list[Message] = storage.load()

    def send(self, text: str) -> str:
        self.messages.append(Message(role="user", text=text))
        try:
            reply = self.service.send(self.messages)
        except Exception:
            self.messages.pop()
            raise
        self.messages.append(Message(role="model", text=reply))
        self.storage.save(self.messages)
        return reply