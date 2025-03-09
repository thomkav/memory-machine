from datetime import datetime
from typing import Dict, List, Optional

# Mock document store data
mock_documents = {
    "doc1": {
        "id": "doc1",
        "name": "Meeting Notes",
        "content": "Discussion about Q3 roadmap. Need to follow up on customer feedback.",
        "created_at": datetime(2023, 7, 15, 10, 30),
        "updated_at": datetime(2023, 7, 15, 11, 45)
    },
    "doc2": {
        "id": "doc2",
        "name": "Research Paper Ideas",
        "content": "1. Memory optimization in distributed systems\n2. Pattern recognition in unstructured data",
        "created_at": datetime(2023, 8, 2, 14, 20),
        "updated_at": datetime(2023, 8, 5, 9, 15)
    },
    "doc3": {
        "id": "doc3",
        "name": "Project Timeline",
        "content": "Phase 1: Research (2 weeks)\nPhase 2: Development (4 weeks)\nPhase 3: Testing (2 weeks)",
        "created_at": datetime(2023, 8, 10, 16, 0),
        "updated_at": datetime(2023, 8, 10, 16, 0)
    }
}


class DocumentStore:
    """Mock document store service client."""

    def list_documents(self) -> List[Dict]:
        """List all documents."""
        return [doc for doc in mock_documents.values()]

    def get_document(self, doc_id: str) -> Optional[Dict]:
        """Get a document by ID."""
        return mock_documents.get(doc_id)

    def add_document(self, name: str, content: str) -> Dict:
        """Add a new document."""
        doc_id = f"doc{len(mock_documents) + 1}"
        now = datetime.now()
        new_doc = {
            "id": doc_id,
            "name": name,
            "content": content,
            "created_at": now,
            "updated_at": now
        }
        mock_documents[doc_id] = new_doc
        return new_doc

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID."""
        if doc_id in mock_documents:
            del mock_documents[doc_id]
            return True
        return False
