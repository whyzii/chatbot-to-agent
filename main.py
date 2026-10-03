# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
from groq_service import GroqService
from viewmodel import ChatViewModel
from view import TerminalView

load_dotenv()
service = GroqService()
view_model = ChatViewModel(service)
TerminalView(view_model).run()