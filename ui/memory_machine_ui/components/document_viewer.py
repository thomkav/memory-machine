from __future__ import annotations
from datetime import datetime
from typing import Callable, Dict, Optional

import rio

from ..document_store import DocumentStore


class DocumentViewer(rio.Component):
    """
    This component displays the content and metadata of a single document.
    """

    store: DocumentStore
    document_id: str
    document: Optional[Dict] = None
    on_back: Optional[Callable[[], None]] = None

    def __post_init__(self):
        self.load_document()

    def load_document(self):
        """Load the document from the store."""
        self.document = self.store.get_document(self.document_id)

    def format_date(self, dt: datetime) -> str:
        """Format a datetime for display."""
        return dt.strftime("%Y-%m-%d %H:%M")

    def handle_back(self):
        """Handle back button press."""
        if self.on_back:
            self.on_back()

    def build(self) -> rio.Component:
        if not self.document:
            return rio.Column(
                rio.Text("Document not found"),
                rio.Button("Back to List", on_press=self.handle_back)
            )

        return rio.Column(
            rio.Text(
                self.document["name"],
                font_size=1.8,
                font_weight="bold",
                margin_bottom=0.5
            ),
            rio.Row(
                rio.Text(f"Created: {self.format_date(self.document['created_at'])}",
                         style="dim",
                         font_size=0.8),
                rio.Text(f"Updated: {self.format_date(self.document['updated_at'])}",
                         style="dim",
                         font_size=0.8),
                spacing=2
            ),
            rio.Card(
                rio.Markdown(
                    self.document["content"],
                ),
                color="background",
                grow_y=True,
            ),
            rio.Button("Back to List", on_press=self.handle_back),
            spacing=1,
        )
