from __future__ import annotations

import rio

from .. import components as comps
from ..document_store import DocumentStore


@rio.page(
    name="Document Details",
    url_segment="document/:id",
)
class DocumentViewPage(rio.Component):
    """
    Page for viewing a single document's details.
    """

    store = DocumentStore()
    doc_id = ""

    def navigate_to_list(self):
        """Navigate back to the document list."""
        self.session.navigate_to("/documents")

    def build(self) -> rio.Component:
        return rio.Stack(
            rio.Column(
                comps.DocumentViewer(
                    store=self.store,
                    document_id=self.doc_id,
                    on_back=self.navigate_to_list
                ),
                margin=2,
            )
        )
