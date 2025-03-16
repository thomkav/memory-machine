from __future__ import annotations

import rio

from ..common import make_button, make_text
from ..components.document_list import DocStorePageBase
from ..constants import PageNames, URLSegments
from ..researchers import create_default_researcher


class AgentWorkflowsComponentNames:
    """Component names used in the AgentWorkflows page."""

    HEADER = "header"
    CHAT_HISTORY = "chat_history"
    SUGGESTED_QUESTIONS = "suggested_questions"
    INPUT_AREA = "input_area"

    DISPLAY_ORDER = [
        HEADER,
        CHAT_HISTORY,
        SUGGESTED_QUESTIONS,
        INPUT_AREA,
    ]


@rio.page(
    name=PageNames.AGENT_WORKFLOWS,
    url_segment=URLSegments.WORKFLOWS_PATH,
)
class AgentWorkflowsPage(DocStorePageBase):
    """
    Page for triggering agent workflows.
    """

    response_text: str = ""
    user_message: str = ""
    chat_history: list = []
    suggested_questions: list = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create a default researcher instance
        self.researcher = create_default_researcher()

        # Initialize chat history with researcher's greeting
        initial_message = self.researcher.get_initial_message()
        if initial_message:
            self.chat_history = [{"role": "assistant", "content": initial_message.chat_message}]
            self.suggested_questions = initial_message.suggested_user_questions

    def trigger_agent_workflow(self, *args):
        """
        Trigger the researcher agent with the user's message.
        """
        if not self.user_message.strip():
            self.response_text = "Please enter a message first."
            return

        # Add user message to chat history
        self.chat_history.append({"role": "user", "content": self.user_message})

        # Process the message with the researcher
        response = self.researcher.process_message(self.user_message)

        # Update UI state
        self.chat_history.append({"role": "assistant", "content": response.chat_message})
        self.suggested_questions = response.suggested_user_questions
        self.response_text = response.chat_message
        self.user_message = ""  # Clear input field

        self.force_refresh()

    def use_suggested_question(self, question: str):
        """
        Use one of the suggested questions as input.
        """
        self.user_message = question
        self.trigger_agent_workflow()

    def _update_user_message(self, event: rio.TextInputChangeEvent):
        """Update the user message value."""
        self.user_message = event.text
        self.force_refresh()

    def _build_chat_message(self, message: dict) -> rio.Component:
        """Build a component for a single chat message."""
        is_user = message["role"] == "user"
        return rio.Container(
            rio.Column(
                make_text(
                    "You:" if is_user else "Researcher:"
                ),
                make_text(message["content"]),
                spacing=1,
            ),
        )

    def _build_suggested_question(self, question: str) -> rio.Component:
        """Build a component for a suggested question."""
        return make_button(
            content=question,
            on_press=lambda: self.use_suggested_question(question),
            grow_x=True,
        )

    def _create_header_component(self) -> rio.Component:
        """Create the header component."""
        return make_text("Agent Workflows")

    def _create_chat_history_component(self) -> rio.Component:
        """Create the chat history component."""
        return rio.Container(
            rio.Column(
                *[self._build_chat_message(msg) for msg in self.chat_history],
                spacing=2,
            ),
            grow_x=True,
        )

    def _create_suggested_questions_component(self) -> rio.Component:
        """Create the suggested questions component."""

        suggested_questions = [
            self._build_suggested_question(q) for q in self.suggested_questions
        ]
        if not suggested_questions:
            return rio.Container(
                make_text("No suggested questions available."),
                grow_x=True,
            )

        return rio.Container(
            rio.Column(
                make_text("Suggested questions:"),
                rio.Column(
                    *[self._build_suggested_question(q) for q in self.suggested_questions],
                    spacing=1,
                ),
                spacing=2,
            ),
            grow_x=True,
            margin_y=10,
        )

    def _create_input_area_component(self) -> rio.Component:
        """Create the input area component."""
        return rio.Row(
            rio.TextInput(
                text="",
                on_change=self._update_user_message,
                label="Type your message here...",
                on_confirm=self.trigger_agent_workflow,
                grow_x=True,
            ),
            make_button(
                content="Send",
                on_press=self.trigger_agent_workflow,
            ),
            spacing=2,
            grow_x=True,
        )

    def _generate_components(self) -> dict[str, rio.Component]:
        """Generate all components used in the interface."""
        return {
            AgentWorkflowsComponentNames.HEADER: self._create_header_component(),
            AgentWorkflowsComponentNames.CHAT_HISTORY: self._create_chat_history_component(),
            AgentWorkflowsComponentNames.SUGGESTED_QUESTIONS: self._create_suggested_questions_component(),
            AgentWorkflowsComponentNames.INPUT_AREA: self._create_input_area_component(),
        }

    def build(self) -> rio.Component:
        """Build the agent workflows page."""
        components = self._generate_components()

        ordered_components = [
            components[name] for name in AgentWorkflowsComponentNames.DISPLAY_ORDER
        ]

        return rio.Column(
            *ordered_components,
            grow_x=True,
            spacing=3,
        )
