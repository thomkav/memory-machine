from openai import Client as OpenAIClient
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)
from typing import List, Optional
from pydantic import BaseModel
from llm import LLMProvider, OpenAIConfig
from conversation import ChatMessage, ChatRole


class LLMChatClient:
    """LLMChatParticipant class that represents an AI agent in the chat."""

    role = ChatRole.ASSISTANT
    instructions: str = "Always respond with the same response: 'Hello, world!'"
    context: dict = {}
    llm_provider: str = LLMProvider.OPENAI
    openai_config: OpenAIConfig = OpenAIConfig()
    openai_client: Optional[OpenAIClient] = None

    def __init__(self):
        """Initialize the LLMChatParticipant with the given configuration."""
        self.openai_client = OpenAIClient(api_key=self.openai_config.api_key)

    def _respond_with_openai(
        self,
        message: str,
    ) -> str:

        """Process a user message using the OpenAI API."""
        assert self.openai_client is not None, "OpenAI client is not initialized."

        completion = self.openai_client.chat.completions.create(
            model=self.openai_config.model,
            messages=[
                ChatCompletionSystemMessageParam(
                    role=ChatRole.SYSTEM,
                    content=self.instructions
                ),
                ChatCompletionUserMessageParam(
                    role=ChatRole.USER,
                    content=message
                ),
            ],
            max_tokens=self.openai_config.max_tokens,
            temperature=self.openai_config.temperature
        )

        response = completion.choices[0].message.content
        assert response is not None, "Response content is empty."

        return response

    def process_message(self, message: str) -> str:
        """Process a message and generate a response."""
        if self.llm_provider == LLMProvider.OPENAI:
            assert self.openai_client is not None, "OpenAI client is not initialized."
            response = self._respond_with_openai(
                message=message,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")

        return response

    def reply(self, chat_messages: List[ChatMessage]) -> ChatMessage:
        """Generate a response based on the chat history."""
        # This method should be implemented in subclasses

        message = chat_messages[-1].content
        if not message:
            raise ValueError("Message is empty.")

        response = self.process_message(message)
        if not response:
            raise ValueError("Response is empty.")

        # Create a new ChatMessage object with the response
        message = ChatMessage(
            role=self.role,
            content=response,
            user_input_prefill_options=[]
        )

        return message

    @property
    def client(self):
        """Get the currently configured LLM client."""
        if self.llm_provider == LLMProvider.OPENAI:
            return self.openai_client
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")


class ResearcherConfig(BaseModel):
    """Configuration class for the Researcher agent."""

    name: str = "LazyResearcher"
    instructions: str = "After replying using your agent, append an additional message, 'Goodbye!'"
    memory: dict = {}
    llm_provider: str = LLMProvider.OPENAI
    openai_config: OpenAIConfig = OpenAIConfig()


class Researcher(BaseModel):
    """
    Researcher class that employs an AI agent to assist users in their research.
    """

    name: str = "LazyResearcher"
    instructions: str = "After replying using your agent, spin up an agent to append an additional message, 'Goodbye!'"
    memory: dict = {}

    @property
    def chat_client(self) -> LLMChatClient:
        """Get the currently configured LLM client."""
        return LLMChatClient()

    def __init__(self, config: Optional[ResearcherConfig] = None):
        """Initialize the researcher with the given configuration."""

        if config:
            self.name = config.name
            self.instructions = config.instructions
            self.memory = config.memory

    def reply(
        self,
        messages: list[ChatMessage]
    ) -> list[ChatMessage]:
        """Generate any number of messages based on the chat history."""

        responses: list[ChatMessage] = []

        llm_chat_client = LLMChatClient()

        chat_client_message = llm_chat_client.reply(
            chat_messages=messages
        )
        responses.append(chat_client_message)

        return responses
