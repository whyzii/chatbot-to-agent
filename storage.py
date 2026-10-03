import json
from dataclasses import asdict
from pathlib import Path
from models import Message

class ChatStorage:
    def __init__(self, filename: str = "history.json"):
        # always save next to this file, no matter where you run the program from
        self.path = Path(__file__).parent / filename

    def load(self) -> list[Message]:
        if not self.path.exists():
            return []
        data = json.loads(self.path.read_text())
        return [Message(**m) for m in data]

    def save(self, messages: list[Message]):
        data = [asdict(m) for m in messages]
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False))