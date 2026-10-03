# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
from groq_service import GroqService
from viewmodel import ChatViewModel
from view import TerminalView
from storage import ChatStorage


load_dotenv()
service = GroqService()
storage = ChatStorage()
view_model = ChatViewModel(service, storage)
TerminalView(view_model).run()