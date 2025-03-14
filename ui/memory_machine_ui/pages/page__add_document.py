from __future__ import annotations

import rio

from ..common import DocStorePageBase
from ..components import DocumentEditor


@rio.page(
    name="Add Document",
    url_segment="document/new",
)
class DocumentAddPage(DocStorePageBase):
    """
    Page for adding a new document to the store.
    """

    def navigate_to_list(self):
        """Navigate back to the document list."""
        self.navigator.to_document_list()

    def build(self) -> rio.Component:
        return rio.Stack(
            rio.Column(
                DocumentEditor(
                    store=self.doc_store,
                    on_save=self.navigator.to_document_list,
                    on_cancel=self.navigator.to_document_list,
                ),
                grow_x=True,
                margin=3
            )
        )
