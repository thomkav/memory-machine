from __future__ import annotations

import rio

from ..components import DocumentViewer
from ..document import DocumentStore


@rio.page(
    name="Document Details",
    url_segment="document/{doc_id}",
)
class DocumentViewPage(rio.Component):
    """
    Page for viewing a single document's details.
    """

    store = DocumentStore()
    doc_id: int

    def navigate_to_list(self):
        """Navigate back to the document list."""
        self.session.navigate_to("/documents")

    def build(self) -> rio.Component:
        return rio.Stack(
            rio.Column(
                DocumentViewer(
                    store=self.store,
                    doc_id=self.doc_id,
                    on_back=self.navigate_to_list
                ),
                margin=2,
            )
        )
