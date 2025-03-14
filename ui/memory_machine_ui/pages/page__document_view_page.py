from __future__ import annotations

import rio

from ..document import InRepoLocalFilesystemDocumentStore, SupportedDocStore
from ..navigation import Navigator


from ..constants import URLSegments
from ..components import (
    DocumentViewer,
)


@rio.page(
    name="Document Details",
    url_segment=URLSegments.DOCUMENT_VIEW_PATTERN,
)
class DocumentViewPage(rio.Component):
    """
    Page for viewing a single document's details.
    """
    doc_id: int
    doc_store: SupportedDocStore = InRepoLocalFilesystemDocumentStore(
        namespace="default",
    )
    navigator: Navigator = Navigator()

    def navigate_to_document_list(self):
        """Navigate back to the document list."""
        self.navigator.to_document_list()

    def build(self) -> rio.Component:
        return DocumentViewer(
            doc_store=self.doc_store,
            doc_id=self.doc_id,
            on_back=self.navigate_to_document_list,
        )
