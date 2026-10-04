from viewmodel import ChatViewModel
import json


class TerminalView:
    def __init__(self, view_model: ChatViewModel):
        self.vm = view_model
    def read_message(self) -> str:
        print("You (paste text, then type END on a new line):")
        lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        return "\n".join(lines).strip()

    def run(self):
        print("Chatbot ready. Type 'quit' to exit.\n")
        while True:
            text = self.read_message()
            if text.lower() == "quit":
                break
            if not text:
                continue
            try:
                self.show(self.vm.send(text))
            except Exception as e:
                print(f"Bot: Sorry, something went wrong ({e}). Try again.\n")

    def show(self, reply: str):
        try:
            item = json.loads(reply)
        except json.JSONDecodeError:
            print(f"Bot: {reply}\n")   # not JSON, show as normal text
            return

        print(f"\nDecision: {item.get('decision')} ({item.get('reason')})")
        if item.get("decision") == "publish":
            print(f"[{item.get('category')} | {item.get('status')}]")
            print(f"\n{item.get('title')}\n")
            print(item.get("summary"))
            print(f"\nWhy it matters: {item.get('why_it_matters')}")
            print(f"Source: {item.get('source_url')}")
        print()