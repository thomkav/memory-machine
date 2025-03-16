from pathlib import Path


class UIDefs:

    ALIGN_XY = 0.5  # Centered


class FilePaths:
    REPO_ROOT_DIR = Path(__file__).parent.parent

    MOCK_DOC_STORE_DIR = REPO_ROOT_DIR / "mock_doc_store"


class URLSegments:

    DOCUMENT_PREFIX = "document"
    DOCUMENT_PATH = DOCUMENT_PREFIX
    DOCUMENT_ADD_PATH = DOCUMENT_PATH + "/new"

    DOCUMENT_VIEW_PATTERN = DOCUMENT_PREFIX + "/{doc_id}"

    @staticmethod
    def document_view_path(doc_id: int) -> str:
        return URLSegments.DOCUMENT_VIEW_PATTERN.format(doc_id=doc_id)

    WORKFLOWS_PREFIX = "workflows"
    WORKFLOWS_PATH = WORKFLOWS_PREFIX
    WORKFLOWS_TRIGGER_PATH = WORKFLOWS_PREFIX + "/trigger"

    WORKFLOWS_TRIGGER_PATTERN = WORKFLOWS_PREFIX + "/trigger/{workflow_id}"


class PageNames:

    ADD_DOCUMENT = "Add Document"
    DOCUMENT_LIST = "Document List"
    VIEW_DOCUMENT = "View Document"
    AGENT_WORKFLOWS = "Agent Workflows"


class Namespaces:

    DEFAULT = "default"
