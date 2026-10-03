from viewmodel import ChatViewModel

class TerminalView:
    def __init__(self, view_model: ChatViewModel):
        self.vm = view_model

    def run(self):
        print("Chatbot ready. Type 'quit' to exit.\n")
        while True:
            text = input("You: ").strip()
            if text.lower() == "quit":
                break
            if not text:
                continue
            try:
                print(f"Bot: {self.vm.send(text)}\n")
            except Exception as e:
                print(f"Bot: Sorry, something went wrong ({e}). Try again.\n")