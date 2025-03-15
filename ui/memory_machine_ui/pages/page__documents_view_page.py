from __future__ import annotations

import rio


from ..components import (
    DocumentStoreDocList,
    DocStorePageBase,
)
from ..document import InRepoLocalFilesystemDocumentStore
from ..navigation import Navigator


@rio.page(
    name="Document List",
    url_segment="documents",
)
class DocumentListPage(DocStorePageBase):
    """
    Page for viewing a list of documents in the store.
    """

    def __init__(self) -> None:
        navigator = Navigator()
        super().__init__(
            doc_store=InRepoLocalFilesystemDocumentStore(
                namespace="default",
            ),
            navigator=navigator,
        )

    def __post_init__(self):
        self.navigator = Navigator(self.session)

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
        return rio.Column(
            DocumentStoreDocList(
                doc_store=self.doc_store,
                on_add_document=self.handle_add_document,
                on_delete_document=self.handle_delete_document,
                on_view_document=self.handle_view_document,
            ),
            margin=1,
        )
