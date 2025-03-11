from __future__ import annotations

import rio

from .. import components as comps
from ..document import DocumentStore


@rio.page(
    name="Document List",
    url_segment="documents",
)
class DocumentListPage(rio.Component):
    """
    Page for viewing a list of documents in the store.
    """

    store = DocumentStore()

    def navigate_to_add(self):
        """Navigate to the document add page."""
        self.session.navigate_to("/document/new")

    def navigate_to_view(self, doc_id: int):
        """Navigate to the document view page."""
        self.session.navigate_to(f"/document/{doc_id}")

    def build(self) -> rio.Component:
        return rio.Stack(
            rio.Column(
                comps.DocumentList(
                    store=self.store,
                    on_add_document=self.navigate_to_add,
                    on_select_document=self.navigate_to_view
                ),
                margin=1,
            )
        )
