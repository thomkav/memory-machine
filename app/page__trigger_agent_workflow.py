from __future__ import annotations

from enum import Enum

import rio

from ..app.components import DocStorePageBase

from .chat import ChatMessage
from .common import make_button, make_text
from .constants import PageNames, URLSegments
from .researcher_agents import Researcher, get_default_researcher


class AgentWorkflowsComponentNames(Enum):
    """Component names used in the AgentWorkflows page."""

    HEADER = "header"
    CHAT_HISTORY = "chat_history"
    SUGGESTED_QUESTIONS = "suggested_questions"
    INPUT_AREA = "input_area"


DISPLAY_ORDER = [
    # HEADER,
    AgentWorkflowsComponentNames.CHAT_HISTORY,
    # SUGGESTED_QUESTIONS,
    # INPUT_AREA,
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
    user_input_prefill_options: list[str] = []
    researcher: Researcher = get_default_researcher()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def trigger_agent_workflow(self, *args):
        """
        Trigger the researcher agent with the user's message.
        """

        self.force_refresh()

    def _update_user_message(self, message: str) -> None:
        """
        Update the user message and refresh the chat interface.
        """
        self.user_message = message
        self.force_refresh()

    def _build_chat_message(self, chat_message: ChatMessage) -> rio.Component:

        return rio.Container(
            rio.Column(
                make_text(str(chat_message)),
                spacing=1,
            ),
        )

    def _create_header_component(self) -> rio.Component:
        """Create the header component."""
        return make_text("Agent Workflows")

    def _create_chat_history_component(self) -> rio.Component:
        """Create the chat history component."""
        return rio.Container(
            rio.Column(
                rio.Text("Not implemented yet."),
                spacing=2,
            ),
            grow_x=True,
        )

    def _build_suggested_question(self, question: str) -> rio.Component:
        """Build component for a suggested question."""
        return rio.Container(
            make_button(
                content=question,
                on_press=lambda: self._update_user_message(question),
                grow_x=True,
            ),
            margin_y=5,
        )

    def _create_suggested_questions_component(self) -> rio.Component:
        """Create the suggested questions component."""

        suggested_questions = [
            self._build_suggested_question(q) for q in self.user_input_prefill_options
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
                    *[self._build_suggested_question(q) for q in self.user_input_prefill_options],
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
                on_change=lambda text_input_event: self._update_user_message(text_input_event.text),
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

    def _generate_components(self) -> dict[AgentWorkflowsComponentNames, rio.Component]:
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
            components[name] for name in DISPLAY_ORDER
        ]

        return rio.Column(
            *ordered_components,
            grow_x=True,
            spacing=3,
        )
