from typing import Callable

from openai import Client as OpenAIClient
from openai.types.chat import (
    ChatCompletionUserMessageParam,
)
from pydantic import BaseModel

from app.custom_logging import LOGGER

from .chat import ChatMessage, ChatRole
from .instructions import Context, InstructionNames, generate_instructions
from .llm import OpenAIConfig


def get_openai_client() -> tuple[OpenAIClient, OpenAIConfig]:
    """Get the OpenAI client instance."""
    config = OpenAIConfig()
    client = OpenAIClient(api_key=config.api_key)
    return client, config


def default_instructions(*args) -> str:
    """Generate default instructions for the researcher agent."""
    return (
        "After replying using your agent, spin up an agent to append an additional message, 'Goodbye!'"
    )


class Researcher(BaseModel):
    """
    Researcher class that employs an AI agent to assist users in their research.
    """

    name: str = "LazyResearcher"
    description: str = "This researcher has simple instructions and needs to be configured."
    instructions_generator: Callable[[Context], str] = default_instructions

    def reply(
        self,
        messages: list[ChatMessage],
        context: Context,
    ) -> list[ChatMessage]:
        """Generate any number of messages based on the chat history."""

        responses: list[ChatMessage] = []

        instructions = self.instructions_generator(context)
        LOGGER.debug(f"Generated instructions: {instructions}")

        client, config = get_openai_client()
        completion = client.chat.completions.create(
            model=config.model,
            messages=[
                ChatCompletionUserMessageParam(
                    role=ChatRole.USER,
                    content=instructions
                ),
            ],
            max_tokens=config.max_tokens,
            temperature=config.temperature
        )

        response = completion.choices[0].message.content
        assert response is not None, "Response content is empty."
        LOGGER.debug(f"OpenAI response: {response}")

        responses.append(
            ChatMessage(
                role=ChatRole.ASSISTANT,
                content=response,
            )
        )

        return responses


class Researchers:
    """
    Enumeration of available researchers.
    """

    LAZY = Researcher(
        name="LazyResearcher",
        description="This researcher has simple instructions and needs to be configured.",
        instructions_generator=default_instructions,
    )

    SUMMARIZER = Researcher(
        name="Summarizer",
        description="This researcher summarizes text.",
        instructions_generator=lambda context: generate_instructions(
            InstructionNames.SUMMARIZE_DOCUMENT,
            context=context,
        ),
    )


def get_default_researcher() -> Researcher:
    """Get the default researcher instance."""
    return Researchers.SUMMARIZER
