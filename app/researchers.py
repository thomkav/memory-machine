import os
import instructor
import openai
from typing import List, Optional
from pydantic import Field, BaseModel
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from atomic_agents.lib.components.agent_memory import AgentMemory
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseAgentInputSchema
from atomic_agents.lib.base.base_io_schema import BaseIOSchema


class ChatMessageSchema(BaseIOSchema):
    """Schema for chat messages exchanged between users and researchers."""

    chat_message: str = Field(
        ...,
        description="The chat message content."
    )
    suggested_user_questions: List[str] = Field(
        default_factory=list,
        description="A list of suggested follow-up questions."
    )

    @classmethod
    def from_history(cls, history_object: dict) -> 'ChatMessageSchema':
        """Create a ChatMessageSchema instance from a chat object."""
        role = history_object.get("role")
        content = history_object.get("content")
        assert role
        assert content
        if isinstance(content, str):
            return cls(chat_message=content, suggested_user_questions=[])

        chat_message = content.get("chat_message")
        suggested_user_questions = content.get("suggested_user_questions")
        assert chat_message
        assert suggested_user_questions

        return cls(chat_message=chat_message, suggested_user_questions=suggested_user_questions)


class ResearcherConfig(BaseModel):
    """Configuration for a researcher agent."""

    name: str
    description: str
    background: List[str]
    steps: List[str]
    output_instructions: List[str]
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 500
    api_key: Optional[str] = None


class Researcher:
    """
    Researcher class that encapsulates an AI agent for assisting with research tasks.
    Designed to be used in UI components.
    """

    def __init__(self, config: ResearcherConfig):
        """Initialize a researcher agent with the given configuration."""
        self.config = config
        self.api_key = config.api_key or os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError("API key not provided in config or environment variable OPENAI_API_KEY")

        # Initialize memory and populate with initial message
        self.memory = AgentMemory()
        self._initialize_memory()

        # Set up OpenAI client
        self.client = instructor.from_openai(openai.OpenAI(api_key=self.api_key))

        # Configure system prompt
        self.prompt_generator = SystemPromptGenerator(
            background=config.background,
            steps=config.steps,
            output_instructions=config.output_instructions,
        )

        # Initialize the agent
        self.agent = BaseAgent(
            config=BaseAgentConfig(
                client=self.client,
                model=config.model,
                system_prompt_generator=self.prompt_generator,
                memory=self.memory,
                input_schema=BaseAgentInputSchema,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                model_api_parameters={"max_tokens": config.max_tokens},
                output_schema=ChatMessageSchema,
            )
        )

    def _initialize_memory(self):
        """Initialize the agent's memory with a greeting message."""
        initial_message = ChatMessageSchema(
            chat_message=f"Hello! I'm {self.config.name}, a researcher assistant. How can I help you today?",
            suggested_user_questions=["What can you help me with?", "How do you work?", "Tell me about your capabilities"]
        )
        self.memory.add_message("assistant", initial_message)

    def get_initial_message(self) -> ChatMessageSchema:
        """Retrieve the initial greeting message from memory."""
        history = self.memory.get_history()
        if history:
            return ChatMessageSchema.from_history(history[0])
        return ChatMessageSchema(chat_message="This is the beginning of a new conversation.")

    def process_message(self, message: str) -> ChatMessageSchema:
        """Process a user message and return the researcher's response."""
        response = self.agent.run(BaseAgentInputSchema(chat_message=message))
        return ChatMessageSchema.from_history(response)

    def get_conversation_history(self) -> List[dict]:
        """Get the full conversation history."""
        return self.memory.get_history()


def create_default_researcher() -> Researcher:
    """Factory function to create a default researcher instance."""
    config = ResearcherConfig(
        name="Research Assistant",
        description="A helpful research assistant that can answer questions and provide information.",
        background=[
            "This assistant is a knowledgeable researcher designed to support users in finding information.",
            "It has access to a wide range of knowledge and can analyze documents to provide insights."
        ],
        steps=[
            "Listen carefully to the user's query or problem.",
            "Analyze the context and identify the core information need.",
            "Provide a clear, concise response with relevant information.",
            "Suggest useful follow-up questions to deepen the investigation."
        ],
        output_instructions=[
            "Keep responses informative but concise.",
            "Cite sources where appropriate.",
            "Include 2-3 relevant follow-up questions that might help the user explore the topic further."
        ]
    )

    return Researcher(config)
