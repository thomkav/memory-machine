
from enum import Enum
from typing import List
from pydantic import BaseModel


class ChatRole(str, Enum):
    """Enumeration of chat roles."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FUNCTION = "function"
    TOOL = "tool"


class ChatMessage(BaseModel):
    """Schema for chat messages exchanged between users and researchers."""

    name: str
    role: ChatRole
    content: str
    user_input_prefill_options: List[str] = []

    # Optional: Add a timestamp or other metadata if needed
    def __str__(self):
        return f"{self.role}: {self.content}"


class Conversation(BaseModel):
    """Conversation class that encapsulates the chat history and context."""

    history: List[ChatMessage] = []
    context: dict = {}

    def add_message(self, message: ChatMessage):
        """Add a message to the conversation history."""
        self.history.append(message)
