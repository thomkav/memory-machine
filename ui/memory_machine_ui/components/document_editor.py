from __future__ import annotations
from typing import Callable, Optional

import rio

from ..document_store import DocumentStore


class DocumentEditor(rio.Component):
    """
    This component provides a form for creating new documents.
    """

    store: DocumentStore
    name: str = ""
    content: str = ""
    on_save: Optional[Callable[[], None]] = None
    on_cancel: Optional[Callable[[], None]] = None

    def on_name_change(self, event: rio.MultiLineTextInputChangeEvent):
        # This function will be called whenever the input's value
        # changes. We'll display the new value in addition to updating
        # our own attribute.
        self.name = event.text

    def on_content_change(self, event: rio.MultiLineTextInputChangeEvent):
        # This function will be called whenever the input's value
        # changes. We'll display the new value in addition to updating
        # our own attribute.
        self.content = event.text

    def handle_save(self):
        """Handle saving the document."""
        if self.name:
            self.store.add_document(self.name, self.content)
            if self.on_save:
                self.on_save()

    def handle_cancel(self):
        """Handle cancelling the operation."""
        if self.on_cancel:
            self.on_cancel()

    def build(self) -> rio.Component:
        return rio.Column(
            rio.Text("Add New Document", font_size=1.8, font_weight="bold"),
            rio.Column(
                rio.MultiLineTextInput(
                    text=self.name,
                    auto_adjust_height=False,
                    on_change=self.on_name_change,
                    label="Enter document title..."
                ),
                rio.MultiLineTextInput(
                    text=self.content,
                    auto_adjust_height=False,
                    on_change=self.on_content_change,
                    label="Enter document content...",
                ),
            ),
            rio.Row(
                rio.Button(
                    "Save",
                    on_press=self.handle_save,
                    is_sensitive=bool(self.name and self.content),
                ),
                rio.Button("Cancel",
                           on_press=self.handle_cancel),
            ),
        )
