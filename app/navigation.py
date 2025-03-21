"""
Utility module to navigate between pages.
"""

from typing import Optional

from rio.session import Session

from .constants import URLSegments
from .document import DocID


def _ensure_path_is_absolute(url_segment: str) -> str:
    if url_segment.startswith('/'):
        return url_segment
    else:
        return "/" + url_segment


class Navigator:
    """
    Utility class for navigating between pages.
    """

    def __init__(self, session: Optional[Session] = None) -> None:
        self.session = session

    def _navigate_to(
        self,
        url_segment: str
    ) -> None:
        assert self.session is not None
        self.session.navigate_to(
            _ensure_path_is_absolute(url_segment=url_segment)
        )

    def to_document_list(self):
        """Navigate to the document list page."""
        self._navigate_to(
            url_segment=URLSegments.DOCUMENT_PREFIX
        )

    def to_document_add(self):
        self._navigate_to(
            url_segment=URLSegments.DOCUMENT_ADD_PATH
        )

    def to_document_view(self, doc_id: DocID):
        self._navigate_to(
            url_segment=URLSegments.document_view_path(
                doc_id=doc_id,
            )
        )
