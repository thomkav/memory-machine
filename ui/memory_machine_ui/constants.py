from pathlib import Path


class UIDefs:

    ALIGN_XY = 0.5  # Centered


class FilePaths:
    UI_ROOT_DIR = Path(__file__).parent.parent

    UI_LOCAL_DOC_EXPORT_DIR = UI_ROOT_DIR / "mock_doc_store"


class URLSegments:

    DOCUMENT_PREFIX = "document"
    DOCUMENT_PATH = DOCUMENT_PREFIX
    DOCUMENT_ADD_PATH = DOCUMENT_PATH + "/new"

    DOCUMENT_VIEW_PATTERN = DOCUMENT_PREFIX + "/{doc_id}"

    @staticmethod
    def document_view_path(doc_id: int) -> str:
        return URLSegments.DOCUMENT_VIEW_PATTERN.format(doc_id=doc_id)


class Namespaces:

    DEFAULT = "default"
