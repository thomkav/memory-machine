from __future__ import annotations

from datetime import datetime
from typing import Any, Callable, List, Optional, Tuple

import rio

from ..common import make_button
from ..custom_logging import LOGGER
from ..document import Doc, DocID, InRepoLocalFilesystemDocumentStore, SupportedDocStore
from ..navigation import Navigator


def format_date(dt: datetime) -> str:
    """Format a datetime for display."""
    return dt.strftime("%Y-%m-%d %H:%M")


class DocumentListCopy:

    PAGE_TITLE = "Document List"
    ADD_DOCUMENT_BUTTON_TEXT = "Add Document"
    DELETE_DOCUMENT_BUTTON_TEXT = "Delete Document"
    VIEW_DOCUMENT_BUTTON_TEXT = "View Document"
    REFRESH_DOC_STORE_BUTTON_TEXT = "Refresh Doc Store"
    SAVE_DOCUMENTS_BUTTON_TEXT = "Save Docs"
    NO_DOCUMENTS_TEXT = "No documents found"


class DocumentListComponentNames:

    HEADER = "header"
    # ADD_DOC_BUTTON = "add_document_button"
    # DELETE_DOC_BUTTON = "delete_document_button"
    # VIEW_DOC_BUTTON = "view_document_button"
    # LOAD_DOC_BUTTON = "load_document_button"
    # SAVE_DOC_BUTTON = "save_document_button"
    BUTTON_ROW = "button_row"
    DOCUMENTS = "documents"

    DISPLAY_ORDER = [
        HEADER,
        DOCUMENTS,
        BUTTON_ROW,
    ]


def build_document_card(
    doc: Doc,
    selected_doc_id: Optional[DocID],
    on_select: Callable[[DocID], None],
) -> rio.Component:
    """
    Build a single document card component.

    Args:
        doc: Document data
        index: Index of this document in the list
        selected_index: Currently selected index
        on_select: Callback function when document is selected

    Returns:
        A Card component representing the document
    """

    def select_document():
        assert doc.doc_id
        LOGGER.debug(f"Selected document {doc.doc_id}")
        on_select(doc.doc_id)

    doc_is_selected = doc.doc_id == selected_doc_id

    return rio.Card(
        rio.Row(
            rio.Column(
                rio.Text(
                    text=doc.name,
                    font_weight="bold" if doc_is_selected else "normal",
                    grow_x=True
                ),
                rio.Text(
                    text=f"Updated: {format_date(doc.updated_at)}",
                    font_size=0.8,
                    style="dim"
                ),
            ),
        ),
        color=rio.Color.GREEN if doc_is_selected else rio.Color.BLACK,
        on_press=select_document,
    )


DocumentAction = Callable[[DocID], None]


class DocumentStoreDocList(rio.Component):
    """
    This component displays a list of documents from a single document store.
    It allows selecting a document and provides buttons for common actions.
    """

    doc_store: InRepoLocalFilesystemDocumentStore
    selected_doc_id: Optional[DocID] = None
    on_add_document: Optional[Callable[[], None]] = None
    on_delete_document: Optional[DocumentAction] = None
    on_view_document: Optional[DocumentAction] = None
    on_select_document: Optional[DocumentAction] = None
    debug_output: Any = None

    # Button specifications: (label, handler_method_name, needs_selection)
    BUTTON_SPECS: List[Tuple[str, str, bool]] = [
        (DocumentListCopy.ADD_DOCUMENT_BUTTON_TEXT, "handle_add", False),
        (DocumentListCopy.VIEW_DOCUMENT_BUTTON_TEXT, "handle_view", True),
        (DocumentListCopy.DELETE_DOCUMENT_BUTTON_TEXT, "handle_delete", True),
        (DocumentListCopy.REFRESH_DOC_STORE_BUTTON_TEXT, "handle_refresh_doc_store", False),
        (DocumentListCopy.SAVE_DOCUMENTS_BUTTON_TEXT, "handle_save", False),
        ("Force Refresh", "handle_force_refresh_ui", False),
        ("Doc State", "handle_debug", False),
    ]

    def __post_init__(self):
        self.handle_refresh_doc_store()
        self.force_refresh()

    def handle_select(self, doc_id: DocID):
        """Select a document by index."""
        LOGGER.debug(f"Selecting document {doc_id}")
        self.selected_doc_id = doc_id
        if self.on_select_document:
            self.on_select_document(doc_id)

    def handle_delete(self):
        """Handle document deletion."""
        if self.on_view_document:
            if self.selected_doc_id:
                self.doc_store.delete_document(self.selected_doc_id)
            else:
                self.debug_output = "No document selected."
        self.force_refresh()

    def handle_view(self):
        """Handle document view."""
        if self.on_view_document:
            if self.selected_doc_id:
                self.on_view_document(self.selected_doc_id)
            else:
                self.debug_output = "No document selected."
        self.force_refresh()

    def handle_add(self):
        """Handle document add."""
        if self.on_add_document:
            self.on_add_document()

    def handle_refresh_doc_store(self):
        """Handle document load."""
        self.doc_store.refresh()
        self.force_refresh()

    def handle_save(self):
        self.doc_store.save_all_to_remote()

    def handle_debug(self):
        self.debug_output = self.doc_store.debug_state()
        self.force_refresh()

    def handle_force_refresh_ui(self):
        self.force_refresh()

    def _create_document_cards_component(self) -> rio.Component:
        """Create a list of document card components."""
        LOGGER.debug(f"Creating {len(self.doc_store.get_doc_map())} document cards")
        document_cards = [
            build_document_card(
                doc=doc,
                selected_doc_id=self.selected_doc_id,
                on_select=self.handle_select,
            ) for doc in self.doc_store.get_doc_map().values()
        ]

        return rio.Column(*document_cards)

    def _generate_buttons(self) -> List[rio.Component]:
        """Generate buttons based on button specifications"""
        buttons = []
        for label, handler_name, needs_selection in self.BUTTON_SPECS:
            handler = getattr(self, handler_name)
            is_sensitive = True if not needs_selection else bool(self.selected_doc_id)
            button = make_button(
                content=label,
                on_press=handler,
                is_sensitive=is_sensitive,
            )
            buttons.append(button)

        # Break the buttons into a grid such that no row has more than 3 buttons
        button_rows = []
        current_row = []
        for button in buttons:
            current_row.append(button)
            if len(current_row) == 3:
                button_rows.append(rio.Row(*current_row))
                current_row = []
        if current_row:
            button_rows.append(rio.Row(*current_row))

        # Make into a column
        column = rio.Column(*button_rows)
        return [column]

    def _generate_components(self) -> dict[str, rio.Component]:

        header = rio.Text(
            text=DocumentListCopy.PAGE_TITLE,
            font_size=1.5, font_weight="bold"
        )

        # Generate buttons using the new method
        buttons = self._generate_buttons()
        button_row = rio.Row(
            *buttons,
            spacing=1,
        )

        # if not self.doc_store.get_doc_map():
        #     documents = rio.Text(DocumentListCopy.NO_DOCUMENTS_TEXT)
        # else:
        documents = self._create_document_cards_component()

        return {
            DocumentListComponentNames.HEADER: header,
            DocumentListComponentNames.BUTTON_ROW: button_row,
            DocumentListComponentNames.DOCUMENTS: documents,
        }

    def build(self) -> rio.Component:

        name_to_component = self._generate_components()

        ordered_components = [
            name_to_component[name] for name in DocumentListComponentNames.DISPLAY_ORDER
        ]

        ordered_components.append(
            rio.Text(
                text=str(self.debug_output),
            )
        )

        return rio.Column(
            *ordered_components,
        )


class DocStorePageBase(rio.Component):

    doc_store: SupportedDocStore = InRepoLocalFilesystemDocumentStore(
        namespace="default",
    )
    navigator: Navigator = Navigator()

    def __post_init__(self):

        self.navigator = Navigator(self.session)
        self.doc_store_list = DocumentStoreDocList(
            doc_store=self.doc_store,
        )
