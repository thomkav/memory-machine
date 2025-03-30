import itertools
import json
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

from .constants import FilePaths
from .custom_logging import LOGGER

DOC_FILE_EXT = '.json'


def serialize_datetime(
    datetime: datetime,
) -> str:
    return datetime.isoformat()


class DocEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime):
            return serialize_datetime(datetime=o)

        return o


DocID = int  # Manually typing this for now


@dataclass
class Doc:
    """
    A document as perceived by the UI.
    """

    name: str
    content: str
    doc_id: Optional[DocID] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    namespace: str = 'default'
    tags: list[str] = field(default_factory=list)
    citations: list[str] = field(default_factory=list)
    edit_log: list[str] = field(default_factory=list)

    @property
    def fn(self) -> str:
        return str(self.doc_id) + DOC_FILE_EXT

    def save(self, outdir: Path) -> None:
        path_out = outdir / self.fn
        with open(path_out, 'w') as file:
            print(f"Saving document to {path_out}")
            json.dump(self.__dict__, file, cls=DocEncoder)

    @staticmethod
    def from_dict(kwargs: dict) -> "Doc":

        def cast_key(k: str, f: Callable) -> Any:
            kwargs[k] = f(kwargs[k])

        for key, f in Doc.__dataclass_fields__.items():
            if f.type == DocID:
                cast_key(key, int)
            elif f.type == int:
                cast_key(key, int)
            elif f.type == datetime:
                cast_key(key, datetime.fromisoformat)

        return Doc(**kwargs)

    @staticmethod
    def load_from_path(path: Path) -> "Doc":
        if DOC_FILE_EXT in path.name:
            return Doc.from_dict(json.load(open(path)))
        raise ValueError(f"Invalid file extension: {path.name}")

    def __str__(self) -> str:
        return f"{self.doc_id}: {self.name}"

    def __repr__(self) -> str:
        return self.__str__()


DOCMAP_LIMIT = 100  # Maximum doc count supported in a single map


class DocMapOverflowException(Exception):
    """
    Exception when the DocMap is overflowing
    """


class DocMap(dict[DocID, Doc]):

    def _add(self, doc: Doc):
        if doc.doc_id is None:
            LOGGER.info(f"Generating id for doc {doc.name}")
            doc.doc_id = max(self.keys()) + 1

        self[doc.doc_id] = doc

    def add(self, doc: Doc):
        """
        Add a document to the map. If the document already exists, raise an error.
        If the document is too large, raise an error.
        """

        if len(self) >= DOCMAP_LIMIT:
            raise DocMapOverflowException

        if doc.doc_id is not None and doc.doc_id in self:
            raise ValueError(f"Doc {doc.doc_id} already exists")
        self._add(doc=doc)

    def delete(self, doc_id: DocID):
        if doc_id not in self:
            raise ValueError(f"Doc ID {doc_id} could not be deleted, it doesnt exist in this map")

        self.pop(doc_id)

    def total_size(self) -> int:
        raise NotImplementedError


NAME_CONTENT_SAMPLES = [
    ("Meeting Notes", "# Meeting Notes\nDiscussion about Q3 roadmap. Need to follow up on customer feedback."),
    ("Research Paper Ideas", "Research Paper Ideas\n1. Machine Learning Applications\n2. Data Analysis Techniques"),
    ("Project Timeline", "Project Timeline\nPhase 1: Research (2 weeks)\nPhase 2: Development (4 weeks)\nPhase 3: Testing (2 weeks)"),  # noqa: E501
    ("Ceramic Production", "Ceramic Production\n1. Raw material preparation\n2. Molding\n3. Firing\n4. Glazing\n5. Firing"),
    ("Grocery List", "Grocery List\n1. Milk\n2. Eggs\n3. Bread\n4. Butter\n5. Cheese")
]
# Create an infinite cycle of content samples
NAME_CONTENT_GENERATOR = itertools.cycle(NAME_CONTENT_SAMPLES)


def generate_docs(
    name_and_content: list[tuple[str, str]] = NAME_CONTENT_SAMPLES
) -> list[Doc]:
    """
    Generate sample documents for testing or initialization purposes.

    Args:
        sample_count: Number of sample documents to generate
        name_content_samples: List of (name, content) tuples to use for samples

    Returns:
        Tuple of (list of doc objects, dict of doc objects by ID)
    """
    sample_docs: list[Doc] = [
        Doc(
            name=name,
            content=content,
        )
        for name, content in name_and_content
    ]

    return sample_docs


DocStoreNamespace = str


class DocStore(metaclass=ABCMeta):

    namespace: DocStoreNamespace
    doc_map: DocMap = DocMap()  # Document ID -> Document
    file_map: dict[str, Doc] = {}  # File name -> Document

    def __init__(self, namespace: DocStoreNamespace) -> None:
        assert namespace
        self.namespace = namespace

    @abstractmethod
    def _get_doc_map_from_store(self) -> DocMap:
        ...

    @abstractmethod
    def save_document(self, doc: Doc):
        ...

    def refresh(self) -> None:
        doc_map_remote = self._get_doc_map_from_store()
        self.doc_map.update(doc_map_remote)

    def save_all_to_remote(self) -> None:
        for doc in self.doc_map.values():
            self.save_document(doc=doc)

    def get_doc_map(self, refresh=False) -> DocMap:
        if refresh:
            self.doc_map = self._get_doc_map_from_store()
        return self.doc_map

    def get_document(self, doc_id: DocID) -> Optional[Doc]:
        """Get a document by ID."""
        return self.doc_map.get(doc_id)

    def add_document(
        self,
        name: str,
        content: str,
        doc_id: Optional[DocID] = None,
        file_name: Optional[str] = None,
    ) -> Doc:
        """Add a new document."""

        if file_name:
            if file_name in self.file_map:
                LOGGER.info(f"File name {file_name} already exists, returning existing document")
                return self.file_map[file_name]

        if doc_id is None:
            doc_id = max(self.doc_map.keys(), default=0) + 1
        if doc_id in self.doc_map:
            LOGGER.info(f"Document {doc_id} already exists, returning existing document")
            return self.doc_map[doc_id]

        new_doc = Doc(
            doc_id=doc_id,
            name=name,
            content=content,
        )
        self.doc_map.add(doc=new_doc)

        if file_name:
            self.file_map[file_name] = new_doc

        return new_doc

    def delete_document(self, doc_id: DocID) -> bool:
        try:
            self.doc_map.delete(doc_id=doc_id)
            if doc_id in self.file_map:
                del self.file_map[doc_id]
            LOGGER.info(f"Deleted document {doc_id} from doc map")
            return True
        except Exception as e:
            LOGGER.error(f"Exception deleting doc in namespace {self.namespace}: {e}")
            return False


class LocalFilesystemDocStore(DocStore):

    doc_dir: Path

    def __init__(self, namespace: DocStoreNamespace, local_root_dir: Path):
        self.doc_dir = local_root_dir / namespace
        super().__init__(namespace=namespace)

    def _get_doc_map_from_store(self) -> DocMap:
        for path in self.doc_dir.iterdir():

            # If not a JSON file, skip
            if DOC_FILE_EXT not in path.name:
                LOGGER.debug(f"Skipping file {path} because it is not a JSON file")
                continue

            # Check if file is already in the map
            if path.name in self.file_map:
                LOGGER.debug(f"File {path} already exists in file map, skipping")
                continue

            try:
                doc = Doc.load_from_path(path=path)
                self.doc_map.add(doc=doc)
                self.file_map[path.name] = doc
                LOGGER.debug(f"Loaded document {doc} from path {path}")
            except Exception as e:
                LOGGER.error(f"Doc at path {path} failed to load: {e}")
        return self.doc_map

    def save_document(self, doc: Doc) -> None:
        doc.save(self.doc_dir)


class InRepoLocalFilesystemDocumentStore(LocalFilesystemDocStore):
    """
    A store for managing documents.

    Optimized for in-memory storage and retrieval of documents.

    Suitable for use in a single-user application with a small number of documents,
    such as a personal note-taking app or document viewer.
    """

    next_idx = 0

    def __init__(self, namespace: str):
        super().__init__(namespace, FilePaths.MOCK_DOC_STORE_DIR)

    def seed_db(self):
        docs = generate_docs()
        for doc in docs:
            self.doc_map.add(doc=doc)

    def debug_state(self) -> dict:
        state = {
            "namespace": self.namespace,
            "doc_map": self.doc_map,
            # "doc_dir": self.doc_dir,
            # "next_idx": self.next_idx,
            # "doc_dir_contents": list(self.doc_dir.iterdir()),
            # "doc_map_size": len(self._doc_map),
        }
        LOGGER.debug(f"DocStore {self.namespace} has {len(self.doc_map)} docs")
        return state


class DocStoreRegistry(dict[DocStoreNamespace, DocStore]):

    def register_doc_stores(self, doc_stores: list[DocStore]):
        for doc_store in doc_stores:
            namespace = doc_store.namespace
            if namespace in self:
                raise ValueError(f"Collision on namespace {namespace}")
            self[namespace] = doc_store

    def get_doc_maps(self) -> dict[DocStoreNamespace, DocMap]:

        docs_by_store = {
            doc_store_id: doc_store.get_doc_map()
            for doc_store_id, doc_store in self.items()
        }

        return docs_by_store


SupportedDocStore = InRepoLocalFilesystemDocumentStore
