from pathlib import Path


class UIDef:

    ALIGN_XY = 0.5  # Centered


class FilePaths:
    UI_ROOT_DIR = Path(__file__).parent.parent

    UI_LOCAL_DOC_EXPORT_DIR = UI_ROOT_DIR / "mock_doc_store"
