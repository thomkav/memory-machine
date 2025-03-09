from __future__ import annotations
from dataclasses import field
from datetime import datetime
from typing import Callable, Dict, List, Optional

import rio

from ..document_store import DocumentStore


def format_date(dt: datetime) -> str:
    """Format a datetime for display."""
    return dt.strftime("%Y-%m-%d %H:%M")


def build_document_card(doc: Dict, index: int, selected_index: int, on_select: Callable[[int], None]) -> rio.Component:
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
    return rio.Card(
        rio.Row(
            rio.Column(
                rio.Text(
                    doc["name"],
                    font_weight="bold" if index == selected_index else "normal",
                    grow_x=True
                ),
                rio.Text(
                    f"Updated: {format_date(doc['updated_at'])}",
                    font_size=0.8,
                    style="dim"
                ),
            ),
        ),
        color=rio.Color.GREEN if index == selected_index else rio.Color.BLACK,
        on_press=lambda idx=index: on_select(idx)
    )


class DocumentList(rio.Component):
    """
    This component displays a list of documents from the document store.
    It allows selecting a document and provides buttons for common actions.
    """

    store: DocumentStore
    documents: List[Dict] = field(default_factory=list)
    selected_index: int = -1
    on_select_document: Optional[Callable[[str], None]] = None
    on_add_document: Optional[Callable[[], None]] = None
    on_delete_document: Optional[Callable[[str], None]] = None

    def __post_init__(self):
        self.refresh_documents()

    def refresh_documents(self):
        """Refresh the document list from the store."""
        self.documents = self.store.list_documents()
        if not self.documents:
            self.selected_index = -1
        elif self.selected_index >= len(self.documents):
            self.selected_index = len(self.documents) - 1

    def select_document(self, index: int):
        """Select a document by index."""
        self.selected_index = index
        if self.on_select_document and 0 <= index < len(self.documents):
            doc_id = self.documents[index]["id"]
            self.on_select_document(doc_id)

    def handle_delete(self):
        """Handle document deletion."""
        if 0 <= self.selected_index < len(self.documents):
            doc_id = self.documents[self.selected_index]["id"]
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
                doc,
                i,
                self.selected_index,
                self.select_document
            ) for i, doc in enumerate(self.documents)
        ]

    def build(self) -> rio.Component:
        if not self.documents:
            return rio.Column(
                rio.Text("No documents found"),
                rio.Button("Add Document", on_press=self.handle_add),
                spacing=1
            )

        return rio.Column(
            rio.Text("Document Store", font_size=1.5, font_weight="bold"),
            rio.Column(
                *self.create_document_cards(),
                spacing=0.5
            ),
            rio.Row(
                rio.Button(
                    "Add Document",
                    on_press=self.handle_add,
                    grow_x=False,
                    grow_y=False,
                    align_x=0.5,
                    align_y=0.5,
                ),
                rio.Button(
                    "View Document",
                    on_press=lambda: self.select_document(self.selected_index),
                    is_sensitive=self.selected_index < 0,
                    grow_x=False,
                    grow_y=False,
                    align_x=0.5,
                    align_y=0.5,
                ),
                rio.Button(
                    "Delete Document",
                    on_press=self.handle_delete,
                    is_sensitive=self.selected_index < 0,
                    grow_x=False,
                    grow_y=False,
                    align_x=0.5,
                    align_y=0.5,
                ),
                spacing=1,
                margin_top=1,
            ),
            spacing=1
        )
