from __future__ import annotations

import rio

from ..components.chat_interface import ResearcherChatInterface
from ..components import (
    ChatMessageComponent,
    DocStorePageBase,
    DocumentStoreDocList,
    EmptyChatPlaceholder,
    GeneratingResponsePlaceholder,
)
from ..custom_logging import LOGGER
from ..document import DocID


class ChatPageComponentNames:

    DOCUMENT_LIST = "document_list"

    SHARED_COMPONENTS_DISPLAY_ORDER = [
        DOCUMENT_LIST
    ]

    MESSAGES_CONTAINER = "messages_container"
    USER_INPUT = "user_input"

    EMPTY_CHAT = "empty_chat"


@rio.page(
    name="Researcher Chat",
    url_segment="",
)
class ResearcherChatPage(DocStorePageBase):
    """
    A page for chatting with a researcher agent.
    """

    # Get a single researcher chat interface
    chat_interface: ResearcherChatInterface | None = None

    # This will be used for the text input to store its result in
    user_message_text: str = ""

    document_context: str = ""

    # If this is `True`, the app is currently generating a response. An
    # indicator will be displayed to the user, and the text input will be
    # disabled.
    is_loading: bool = False

    def __post_init__(self):
        self.doc_store.refresh()
        self.chat_interface = ResearcherChatInterface(
            on_message_sent=self.on_text_input_confirm,
        )
        self.chat_interface.set_default_researcher()

    def handle_select(self, doc_id: DocID) -> None:
        doc = self.doc_store.get_document(doc_id=doc_id)
        LOGGER.info(f"Document Selected {doc}")
        assert doc
        self.document_context = f"Document Details: Name: {doc.name}, Content: {doc.content}"

    def handle_enter(self):
        LOGGER.debug("Entered something into the chat.")

        _ = self.on_text_input_confirm()

    async def on_text_input_confirm(self) -> None:
        """
        Called when the text input is confirmed, or the "send" button pressed.
        The function ensures that the input isn't empty. If that's the case the
        message is sent on to the `on_question` function.
        """
        # If the user hasn't typed anything, do nothing
        message_text = self.user_message_text.strip()
        LOGGER.info(f"Received message text {message_text}")

        if not message_text:
            LOGGER.info("No message text")
            return

        # Empty the text input so the user can type another message
        self.user_message_text = ""

        # A question was asked!
        await self.on_question(message_text)

    async def on_question(self, message_text: str) -> None:
        """
        Called whenever the user asks a question. The function adds the user's
        message to the chat history, generates a response, and adds that to the
        chat history as well.
        """
        LOGGER.info(f"Asking question: {message_text}")
        assert self.chat_interface is not None, "Chat interface should be initialized."
        assert self.chat_interface.researcher is not None, "Researcher should be set after initialization."

        # If document context is provided,
        # add it as a unique message
        if self.document_context:
            self.chat_interface.add_system_message(
                message=self.document_context,
            )

        # Indicate to the user that the app is doing something
        self.is_loading = True
        self.force_refresh()

        # Add the user's message to the chat history
        self.chat_interface.add_user_message(
            message=message_text,
        )

        # Generate a response
        try:
            messages = self.chat_interface.researcher.reply(
                messages=self.chat_interface.messages,
            )
            # Add all messages to chat history
            for message in messages:
                self.chat_interface.add_researcher_message(
                    name=self.chat_interface.researcher.name,
                    message=message.content,
                    user_input_prefill_options=message.user_input_prefill_options,
                )

        # Don't get stuck in loading state if an error occurs
        finally:
            self.is_loading = False

    def _create_header_icons(self) -> list[rio.Component]:
        """Create the header icons for the chat page."""
        return [
            rio.Icon(
                "rio/logo:fill",
                min_width=3,
                min_height=3,
                align_x=0,
                margin=2,
                align_y=0,
            ),
            rio.Icon(
                "material/twinkle",
                min_width=3,
                min_height=3,
                align_x=1,
                margin=2,
                align_y=0,
            )
        ]

    def _create_message_components(self) -> list[rio.Component]:
        """Create the message components based on conversation history."""

        # If there is no chat interface, return an empty list
        if not self.chat_interface:
            return []

        message_components: list[rio.Component] = [
            ChatMessageComponent(msg) for msg in self.chat_interface.messages
        ]

        if self.is_loading:
            message_components.append(
                GeneratingResponsePlaceholder(
                    align_x=0.5,
                )
            )

        return message_components

    def _create_messages_container(self, column_width: int, column_align_x: float | None) -> rio.Component:
        """Create the scrollable container for chat messages."""
        message_components = self._create_message_components()

        return rio.ScrollContainer(
            rio.Column(
                # Display the messages
                *message_components,
                # Take up superfluous space
                rio.Spacer(),
                spacing=1,
                # Center the column on wide screens
                margin=2,
                min_width=column_width,
                align_x=column_align_x,
            ),
            grow_y=True,
            scroll_x="never",
        )

    def _create_input_row(self, column_width: int, column_align_x: float | None) -> rio.Component:
        """Create the input row for user messages."""
        return rio.Row(
            rio.MultiLineTextInput(
                label="Ask something...",
                text=self.bind().user_message_text,
                on_confirm=None,
                is_sensitive=not self.is_loading,
                grow_x=True,
                min_height=8,
            ),
            rio.IconButton(
                icon="material/navigate_next",
                min_size=4,
                on_press=self.on_text_input_confirm,
                is_sensitive=not self.is_loading,
                align_y=0.5,
            ),
            spacing=1,
            min_width=column_width,
            margin_bottom=1,
            align_x=column_align_x,
        )

    def _generate_components(self) -> dict[str, rio.Component]:

        components_by_name = {}

        # Center the chat on wide screens
        if self.session.window_width > 40:
            column_width = 40
            column_align_x = 0.5
        else:
            column_width = 0
            column_align_x = None

        components_by_name[
            ChatPageComponentNames.EMPTY_CHAT
        ] = EmptyChatPlaceholder(
            user_message_text=self.user_message_text,
            on_question=self.on_question,
            align_x=0.5,
            align_y=0.5,
        )

        # Messages
        components_by_name[
            ChatPageComponentNames.MESSAGES_CONTAINER
        ] = self._create_messages_container(column_width, column_align_x)

        # User input
        components_by_name[
            ChatPageComponentNames.USER_INPUT
        ] = self._create_input_row(column_width, column_align_x)

        components_by_name[
            ChatPageComponentNames.DOCUMENT_LIST
        ] = rio.Row(
            DocumentStoreDocList(
                doc_store=self.doc_store,
                on_select_document=self.handle_select,
            )
        )

        return components_by_name

    def build(self) -> rio.Component:

        name_to_component = self._generate_components()
        ordered_components = [
            name_to_component[name] for name in ChatPageComponentNames.SHARED_COMPONENTS_DISPLAY_ORDER
        ]

        # If there aren't any messages yet, display a placeholder
        if not self.chat_interface or not self.chat_interface.messages:
            ordered_components.append(
                name_to_component[ChatPageComponentNames.EMPTY_CHAT]
            )
        else:
            ordered_components.extend([
                name_to_component[ChatPageComponentNames.MESSAGES_CONTAINER],
                name_to_component[ChatPageComponentNames.USER_INPUT],
            ])

        # Combine everything into a neat package
        return rio.Stack(
            *self._create_header_icons(),
            rio.Column(
                *ordered_components,
                spacing=0.5,
            ),
        )
