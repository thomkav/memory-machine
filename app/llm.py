"""
LLM (Large Language Model) configuration for the researcher agent.
"""

from enum import Enum
import os
from typing import Optional
from pydantic import BaseModel


class LLMProvider(str, Enum):
    """Enumeration of supported language model providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"

    SUPPORTED = [
        OPENAI,
        # ANTHROPIC,  # TODO: Add support for Anthropic API
    ]


class OpenAIConfig(BaseModel):
    """Configuration for a researcher agent."""

    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 500
    api_key: Optional[str] = os.getenv("OPENAI_API_KEY")


class AgentConfig(BaseModel):
    """Configuration for a researcher agent
    that encapsulates information about the agent's capabilities and instructions."""
    name: str
    instructions: str
    description: str = ""
