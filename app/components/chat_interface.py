from typing import Callable
import rio

from ..common import make_button, make_text
from ..conversation import ChatRole, ChatMessage
from ..researcher_agents import Researcher


class ChatInterfaceComponentNames:
    """Component names used in the ChatInterface."""

    CHAT_HISTORY = "chat_history"
    SUGGESTED_QUESTIONS = "suggested_questions"
    INPUT_AREA = "input_area"

    DISPLAY_ORDER = [
        CHAT_HISTORY,
        SUGGESTED_QUESTIONS,
        INPUT_AREA,
    ]


class ChatInterface(rio.Component):
    """
    A reusable chat interface component for interacting with researchers.
    """

    def __init__(
        self,
        on_message_sent: Callable | None = None,
        height: int = 400,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.enabled_researchers: list[Researcher] = []
        self.on_message_sent = on_message_sent
        self.height = height
        self.user_message = ""
        self.messages: list[ChatMessage] = []   
        self.researcher: Researcher | None = None
        self.user_input_prefill_options = []

    def set_researcher(self, researcher: Researcher):
        """Set the researcher for the chat interface."""
        self.researcher = researcher
        self.messages = [ChatMessage(
            name=researcher.name,
            role=ChatRole.SYSTEM,
            content=researcher.instructions
        )]
        self.user_input_prefill_options = []
        self.force_refresh()

    def add_user_message(self, message: str):
        """Add a user message to the chat history."""
        self.messages.append(
            ChatMessage(
                name="User",
                role=ChatRole.USER,
                content=message
            )
        )
        self.force_refresh()

    def add_researcher_message(
        self,
        name: str,
        message: str,
        user_input_prefill_options: list[str] = [],
    ):
        """Add a researcher message to the chat history."""
        self.messages.append(
            ChatMessage(
                name=name,
                role=ChatRole.ASSISTANT,
                content=message
            )
        )
        self.user_input_prefill_options = user_input_prefill_options

        self.force_refresh()

    def send_message(self, *args):
        """Send the current user message to the current researcher."""
        if not self.researcher:
            raise ValueError("No researcher set. Please set a researcher before sending messages.")

        if not self.user_message.strip():
            return

        # Add user message to chat history
        self.add_user_message(message=self.user_message)

        # Call 
        messages = self.researcher.reply(
            messages=self.messages,
        )
        # Add all messages to chat history
        for message in messages:
            self.add_researcher_message(
                name=self.researcher.name,
                message=message.content,
                user_input_prefill_options=message.user_input_prefill_options,
            )

        # Clear input
        message_sent = self.user_message
        self.user_message = ""

        # Call the callback if provided
        if self.on_message_sent:
            self.on_message_sent(message_sent, self.messages)

        self.force_refresh()

    def use_suggested_question(self, question: str):
        """Use a suggested question as the user message."""
        self.user_message = question
        self.send_message()

    def _update_user_message(self, event: rio.TextInputChangeEvent):
        """Update the user message value."""
        self.user_message = event.text
        self.force_refresh()

    def _build_message_component(
        self,
        message: ChatMessage,
    ) -> rio.Component:
        """Build a component for a single chat message."""
        is_user = message.role == ChatRole.USER
        return rio.Container(
            rio.Column(
                rio.Text(
                    "You:" if is_user else "Researcher:",
                ),
                rio.Text(message.content),
                spacing=1,
            ),
        )

    def _build_suggested_question(self, question: str) -> rio.Component:
        """Build a component for a suggested question."""
        return rio.Button(
            rio.Text(question),
            on_press=lambda: self.use_suggested_question(question),
            grow_x=True,
        )

    def _create_chat_history_component(self) -> rio.Component:
        """Create the chat history component."""
        return rio.Container(
            rio.Column(
                *[self._build_message_component(msg) for msg in self.messages],
                spacing=2,
            ),
            grow_x=True,
        )

    def _create_suggested_questions_component(self) -> rio.Component:
        """Create the suggested questions component."""

        return rio.Container(
            rio.Column(
                make_text("Suggested questions:"),
                rio.Column(
                    *[self._build_suggested_question(q) for q in self.user_input_prefill_options],
                    spacing=1,
                ) if self.user_input_prefill_options else make_text("No suggestions available."),
                spacing=2,
            ),
            grow_x=True,
            margin_y=10,
        )

    def _create_input_area_component(self) -> rio.Component:
        """Create the input area component."""
        return rio.Row(
            rio.TextInput(
                text=self.user_message,
                on_change=self._update_user_message,
                label="Type your message here...",
                on_confirm=self.send_message,
                grow_x=True,
            ),
            make_button(
                content="Send",
                on_press=self.send_message,
            ),
            spacing=2,
            grow_x=True,
        )

    def _generate_components(self) -> dict[str, rio.Component]:
        """Generate all components used in the interface."""
        return {
            ChatInterfaceComponentNames.CHAT_HISTORY: self._create_chat_history_component(),
            ChatInterfaceComponentNames.SUGGESTED_QUESTIONS: self._create_suggested_questions_component(),
            ChatInterfaceComponentNames.INPUT_AREA: self._create_input_area_component(),
        }

    def build(self) -> rio.Component:
        """Build the chat interface component."""
        components = self._generate_components()

        ordered_components = [
            components[name] for name in ChatInterfaceComponentNames.DISPLAY_ORDER
        ]

        return rio.Column(
            *ordered_components,
            grow_x=True,
            spacing=3,
        )
