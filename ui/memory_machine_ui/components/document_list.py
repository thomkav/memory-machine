from __future__ import annotations
from dataclasses import field
from datetime import datetime
from typing import Callable, List, Optional

import rio

from .standards import make_button
from ..document import Doc, DocumentStore


def format_date(dt: datetime) -> str:
    """Format a datetime for display."""
    return dt.strftime("%Y-%m-%d %H:%M")


def build_document_card(
    doc: Doc,
    index: int,
    selected_index: int,
    on_select: Callable[[int], None],
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
        on_select(index)

    return rio.Card(
        rio.Row(
            rio.Column(
                rio.Text(
                    doc.name,
                    font_weight="bold" if index == selected_index else "normal",
                    grow_x=True
                ),
                rio.Text(
                    f"Updated: {format_date(doc.updated_at)}",
                    font_size=0.8,
                    style="dim"
                ),
            ),
        ),
        color=rio.Color.GREEN if index == selected_index else rio.Color.BLACK,
        on_press=select_document,
    )


class DocumentList(rio.Component):
    """
    This component displays a list of documents from the document store.
    It allows selecting a document and provides buttons for common actions.
    """

    store: DocumentStore
    docs: List[Doc] = field(default_factory=list)
    selected_index: int = -1
    on_select_document: Optional[Callable[[int], None]] = None
    on_add_document: Optional[Callable[[], None]] = None
    on_delete_document: Optional[Callable[[int], None]] = None

    def __post_init__(self):
        self.refresh_documents()

    def append_refresh(self, callable: Callable) -> Callable:

        def call_then_refresh() -> None:
            callable()
            self.refresh_documents()

        return lambda: call_then_refresh()

    def refresh_documents(self):
        """Refresh the document list from the store."""
        self.docs = self.store.list_documents()
        if not self.docs:
            self.selected_index = -1
        elif self.selected_index >= len(self.docs):
            self.selected_index = len(self.docs) - 1

    def select_document(self, index: int):
        """Select a document by index."""
        self.selected_index = index
        if self.on_select_document and 0 <= index < len(self.docs):
            doc_id = self.docs[index].doc_id
            self.on_select_document(doc_id)

    def handle_delete(self):
        """Handle document deletion."""
        if 0 <= self.selected_index < len(self.docs):
            doc_id = self.docs[self.selected_index].doc_id
            if self.on_delete_document:
                self.on_delete_document(doc_id)

    def handle_add(self):
        """Handle adding a new document."""
        if self.on_add_document:
            self.on_add_document()

    def create_document_cards(self) -> List[rio.Component]:
        """Create a list of document card components."""
        return [
            build_document_card(
                doc=doc,
                index=i,
                selected_index=self.selected_index,
                on_select=self.select_document
            ) for i, doc in enumerate(self.docs)
        ]

    def build(self) -> rio.Component:
        if not self.docs:
            return rio.Column(
                rio.Text("No documents found"),
                rio.Button("Add Document", on_press=self.handle_add),
                spacing=1
            )

        return rio.Column(
            rio.Text(
                text="Document Store",
                font_size=1.5, font_weight="bold"),
            rio.Column(
                *self.create_document_cards(),
                spacing=0.5
            ),
            rio.Row(
                make_button(
                    content="Add Document",
                    on_press=self.handle_add,
                ),
                make_button(
                    content="View Document",
                    on_press=lambda: self.select_document(self.selected_index),
                    is_sensitive=self.selected_index < 0,
                ),
                make_button(
                    content="Delete Document",
                    on_press=self.handle_delete,
                    is_sensitive=self.selected_index < 0,
                ),
                make_button(
                    content="Save Docs",
                    on_press=self.store.save_all,
                ),
                make_button(
                    content="Load Docs",
                    on_press=self.append_refresh(self.store.load_all)
                ),
                spacing=1,
                margin_top=1,
            ),
            spacing=1
        )
