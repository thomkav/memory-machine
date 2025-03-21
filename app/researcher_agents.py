from typing import List

from .llm import LLMProvider, OpenAIConfig
from openai import Client as OpenAIClient
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)
from pydantic import BaseModel, Field

from .chat import ChatMessage, ChatRole


def get_openai_client() -> tuple[OpenAIClient, OpenAIConfig]:
    """Get the OpenAI client instance."""
    config = OpenAIConfig()
    client = OpenAIClient(api_key=config.api_key)
    return client, config


class LLMChatClient(BaseModel):
    """
    LLMChatClient class that encapsulates the logic for interacting with a language model.
    This class is responsible for processing messages and generating responses
    using the specified language model provider.
    """

    name: str = "LazyResearcher"
    description: str = "A lazy researcher agent that always responds with 'Hello, world!'"
    role: ChatRole = Field(
        default=ChatRole.ASSISTANT,
        description="The role of the agent in the chat.",
    )
    instructions: str = "Always respond with the same response: 'Hello, world!'"
    context: dict = Field(
        default_factory=dict,
        description="Context for the agent's responses.",
    )
    llm_provider: str = LLMProvider.OPENAI

    def _respond_with_openai(
        self,
        message: str,
    ) -> str:
        """Process a user message using the OpenAI API."""

        client, config = get_openai_client()
        completion = client.chat.completions.create(
            model=config.model,
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
            max_tokens=config.max_tokens,
            temperature=config.temperature
        )

        response = completion.choices[0].message.content
        assert response is not None, "Response content is empty."

        return response

    def process_message(self, message: str) -> str:
        """Process a message and generate a response."""
        if self.llm_provider == LLMProvider.OPENAI:
            response = self._respond_with_openai(
                message=message,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")

        return response

    def reply(self, chat_messages: List[ChatMessage]) -> ChatMessage:
        """Generate a response based on the chat history."""

        message = chat_messages[-1].content
        if not message:
            raise ValueError("Message is empty.")

        response = self.process_message(message)
        if not response:
            raise ValueError("Response is empty.")

        # Create a new ChatMessage object with the response
        message = ChatMessage(
            name=self.name,
            role=self.role,
            content=response,
            user_input_prefill_options=[]
        )

        return message


class Researcher(BaseModel):
    """
    Researcher class that employs an AI agent to assist users in their research.
    """

    name: str = "LazyResearcher"
    objective: str = "This researcher has simple instructions and needs to be configured."
    instructions: str = "After replying using your agent, spin up an agent to append an additional message, 'Goodbye!'"
    memory: dict = Field(
        default_factory=dict,
        description="Memory for storing conversation context.",
    )

    @property
    def chat_client(self) -> LLMChatClient:
        """Get the currently configured LLM client."""
        return LLMChatClient()

    def reply(
        self,
        messages: list[ChatMessage],
    ) -> list[ChatMessage]:
        """Generate any number of messages based on the chat history."""

        responses: list[ChatMessage] = []

        llm_chat_client = LLMChatClient()

        chat_client_message = llm_chat_client.reply(
            chat_messages=messages
        )
        responses.append(chat_client_message)

        # Add a goodbye message
        goodbye_message = ChatMessage(
            name=self.name,
            role=ChatRole.ASSISTANT,
            content="Goodbye!",
            user_input_prefill_options=[]
        )
        responses.append(goodbye_message)

        return responses
