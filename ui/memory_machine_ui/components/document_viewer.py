from __future__ import annotations
from datetime import datetime
from typing import Callable, Optional

import rio

from ..document import Doc, SupportedDocStore


class DocumentViewer(rio.Component):
    """
    This component displays the content and metadata of a single document.
    """

    doc_store: SupportedDocStore
    doc_id: int
    doc: Optional[Doc] = None
    on_back: Optional[Callable[[], None]] = None

    def __post_init__(self):
        self.load_document()

    def load_document(self):
        """Load the document from the store."""
        self.doc = self.doc_store.get_document(self.doc_id)

    def format_date(self, dt: datetime) -> str:
        """Format a datetime for display."""
        return dt.strftime("%Y-%m-%d %H:%M")

    def handle_back(self):
        """Handle back button press."""
        if self.on_back:
            self.on_back()

    def build(self) -> rio.Component:
        if not self.doc:
            return rio.Column(
                rio.Text("Document not found"),
                rio.Button("Back to List", on_press=self.handle_back)
            )

        return rio.Column(
            rio.Text(
                self.doc.name,
                font_size=1.8,
                font_weight="bold",
                margin_bottom=0.5
            ),
            rio.Row(
                rio.Text(f"Created: {self.format_date(self.doc.created_at)}",
                         style="dim",
                         font_size=0.8),
                rio.Text(f"Updated: {self.format_date(self.doc.updated_at)}",
                         style="dim",
                         font_size=0.8),
                spacing=2
            ),
            rio.Card(
                rio.Markdown(
                    self.doc.content,
                ),
                color="background",
                grow_y=True,
            ),
            rio.Button("Back to List", on_press=self.handle_back),
            spacing=1,
        )
