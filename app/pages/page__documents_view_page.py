from __future__ import annotations

import rio

from ..components import DocStorePageBase


@rio.page(
    name="Document List",
    url_segment="documents",
)
class DocumentListPage(DocStorePageBase):
    """
    Page for viewing a list of documents in the store.
    """

    def handle_add_document(self) -> None:
        """Navigate to the document add page."""
        self.navigator.to_document_add()

    def handle_delete_document(self, doc_id: int) -> None:
        """Handle document deletion."""
        self.doc_store.delete_document(doc_id=doc_id)

    def handle_view_document(self, doc_id) -> None:
        """Navigate to the document view page."""
        self.navigator.to_document_view(doc_id=doc_id)

    def build(self) -> rio.Component:
        assert self.doc_list_component is not None, "Document store list should be initialized."
        return rio.Column(self.doc_list_component)
