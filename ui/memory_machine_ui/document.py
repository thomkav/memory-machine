from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

import json

from .constants import FilePaths

DOC_FILE_EXT = '.doc'


def serialize_datetime(
    datetime: datetime,
) -> str:
    return datetime.isoformat()


class DocEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime):
            return serialize_datetime(datetime=o)

        return o


@dataclass
class Doc:

    doc_id: int
    name: str
    content: str
    created_at: datetime
    updated_at: datetime

    @property
    def fn(self) -> str:
        return str(self.doc_id) + DOC_FILE_EXT

    def save(self, path: Path) -> None:
        with open(path / self.fn, 'w') as file:
            json.dump(self.__dict__, file, cls=DocEncoder)

    @staticmethod
    def from_dict(kwargs: dict) -> "Doc":

        def cast_key(k: str, f: Callable) -> Any:
            kwargs[k] = f(kwargs[k])

        for key, field in Doc.__dataclass_fields__.items():
            if field.type == int:
                cast_key(key, int)
            if field.type == datetime:
                cast_key(key, datetime.fromisoformat)

        return Doc(**kwargs)

    @staticmethod
    def load(path: Path) -> "Doc":
        if DOC_FILE_EXT in path.name:
            return Doc.from_dict(json.load(open(path)))
        raise ValueError


SAMPLE_DOCS: list[Doc] = [
    Doc(
        doc_id=0,
        name="Meeting Notes",
        content="Discussion about Q3 roadmap. Need to follow up on customer feedback.",
        created_at=datetime(2023, 7, 15, 10, 30),
        updated_at=datetime(2023, 7, 15, 11, 45),
    ),
    Doc(
        doc_id=1,
        name="Research Paper Ideas",
        content="1. Memory optimization in distributed systems\n2. Pattern recognition in unstructured data",
        created_at=datetime(2023, 8, 2, 14, 20),
        updated_at=datetime(2023, 8, 5, 9, 15)
    ),
    Doc(
        doc_id=2,
        name="Project Timeline",
        content="Phase 1: Research (2 weeks)\nPhase 2: Development (4 weeks)\nPhase 3: Testing (2 weeks)",
        created_at=datetime(2023, 8, 10, 16, 0),
        updated_at=datetime(2023, 8, 10, 16, 0)
    )
]

SAMPLE_DOCS_BY_ID: dict[int, Doc] = {
    doc.doc_id: doc
    for doc in SAMPLE_DOCS
}


class DocumentStore:
    """Mock document store service client."""

    docs_by_id: dict[int, Doc]
    local_export_dir = FilePaths.UI_LOCAL_DOC_EXPORT_DIR

    def __init__(self) -> None:
        self.docs_by_id = SAMPLE_DOCS_BY_ID

    def save_all(self) -> None:

        for doc in self.docs_by_id.values():
            doc.save(path=self.local_export_dir)

    def load_all(self) -> None:

        for path in self.local_export_dir.iterdir():
            doc = Doc.load(path)
            self.docs_by_id[doc.doc_id] = doc

    def list_documents(self) -> list[Doc]:
        """List all documents."""
        sorted_keys = sorted(self.docs_by_id.keys())
        return [self.docs_by_id[k] for k in sorted_keys]

    def get_document(self, doc_id: int) -> Optional[Doc]:
        """Get a document by ID."""
        return self.docs_by_id.get(doc_id)

    def add_document(self, name: str, content: str) -> Doc:
        """Add a new document."""
        doc_id = max(self.docs_by_id.keys()) + 1
        now = datetime.now()
        new_doc = Doc(
            doc_id=doc_id,
            name=name,
            content=content,
            created_at=now,
            updated_at=now
        )
        self.docs_by_id[doc_id] = new_doc
        return new_doc

    def delete_document(self, doc_id: int) -> bool:
        """Delete a document by ID."""
        if doc_id in self.docs_by_id:
            del self.docs_by_id[doc_id]
            return True
        return False
