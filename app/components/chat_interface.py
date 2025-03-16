from typing import Callable, Optional
import rio

from app.common import make_button, make_text

from ..researchers import Researcher


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
        researcher: Researcher,
        on_message_sent: Optional[Callable] = None,
        height: int = 400,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.researcher = researcher
        self.on_message_sent = on_message_sent
        self.height = height
        self.user_message = ""
        self.chat_history = []
        self.suggested_questions = []

        # Initialize with the first message
        initial_message = self.researcher.get_initial_message()
        if initial_message:
            self.chat_history = [{"role": "assistant", "content": initial_message.chat_message}]
            self.suggested_questions = initial_message.suggested_user_questions

    def send_message(self, *args):
        """Send the current user message to the researcher."""
        if not self.user_message.strip():
            return

        # Add user message to chat history
        self.chat_history.append({"role": "user", "content": self.user_message})

        # Process the message
        response = self.researcher.process_message(self.user_message)

        # Update state
        self.chat_history.append({"role": "assistant", "content": response.chat_message})
        self.suggested_questions = response.suggested_user_questions

        # Clear input
        message_sent = self.user_message
        self.user_message = ""

        # Call the callback if provided
        if self.on_message_sent:
            self.on_message_sent(message_sent, response)

        self.force_refresh()

    def use_suggested_question(self, question: str):
        """Use a suggested question as the user message."""
        self.user_message = question
        self.send_message()

    def _update_user_message(self, event: rio.TextInputChangeEvent):
        """Update the user message value."""
        self.user_message = event.text
        self.force_refresh()

    def _build_message(self, message: dict) -> rio.Component:
        """Build a component for a single chat message."""
        is_user = message["role"] == "user"
        return rio.Container(
            rio.Column(
                rio.Text(
                    "You:" if is_user else "Researcher:",
                ),
                rio.Text(message["content"]),
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
                *[self._build_message(msg) for msg in self.chat_history],
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
                    *[self._build_suggested_question(q) for q in self.suggested_questions],
                    spacing=1,
                ) if self.suggested_questions else make_text("No suggestions available."),
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
