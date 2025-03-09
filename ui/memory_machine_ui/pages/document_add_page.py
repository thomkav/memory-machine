from __future__ import annotations

import rio

from .. import components as comps
from ..document_store import DocumentStore


@rio.page(
    name="Add Document",
    url_segment="document/new",
)
class DocumentAddPage(rio.Component):
    """
    Page for adding a new document to the store.
    """
    store = DocumentStore()

    def navigate_to_list(self):
        """Navigate back to the document list."""
        self.session.navigate_to("/documents")

    def build(self) -> rio.Component:
        return rio.Stack(
            rio.Column(
                comps.DocumentEditor(
                    store=self.store,
                    on_save=self.navigate_to_list,
                    on_cancel=self.navigate_to_list
                ),
                align_x=0.5,
            )
        )
