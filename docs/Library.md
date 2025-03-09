# Library

## Overview
The Library serves as the central repository for all knowledge, documents, and information managed by Memory Machine. It provides a structured way to store, retrieve, and organize various types of content.

## Features
- **Document Management**: Store documents in a quickly readable, flat structure
- **Tagging System**: Apply basic metadata and tags to improve searchability
- **Version Control**: Track changes and maintain document history
- **Search Functionality**: Powerful search capabilities across the entire library
- **Integration**: Seamless integration with other Memory Machine components

## Usage
The Library can be accessed and utilized in various ways:

```python
# Import the Library class
from app.models.library import Library

# Create a new library instance
library = Library()

# Add a document to the library
library.add_document({
    "title": "Research Notes",
    "content": "...",
    "tags": ["research", "notes"]
})

# Retrieve documents by tag
research_docs = library.get_documents_by_tag("research")

# Search across the library
search_results = library.search("quantum computing")
```

## API Reference

### Methods

#### `add_document(document: dict) -> None`
Adds a new document to the library.

#### `get_document(id: str) -> dict or None`
Retrieves a document by its unique identifier.

#### `update_document(id: str, updates: dict) -> None`
Updates an existing document with new information.

#### `delete_document(id: str) -> bool`
Removes a document from the library.

#### `search(query: str) -> list`
Searches for documents matching the provided query.

#### `get_documents_by_tag(tag: str) -> list`
Retrieves all documents that have been tagged with the specified tag.

## Flask API Endpoints

The Library component exposes several RESTful API endpoints:

```
GET /api/library/documents - Get all documents
GET /api/library/documents/<id> - Get a specific document
POST /api/library/documents - Create a new document
PUT /api/library/documents/<id> - Update a document
DELETE /api/library/documents/<id> - Delete a document
GET /api/library/search?q=<query> - Search for documents
GET /api/library/tags/<tag> - Get documents by tag
```

## Best Practices
- Use consistent tagging conventions to improve organization
- Regularly back up the library to prevent data loss
- Implement access controls for sensitive documents
- Use descriptive document titles for better searchability

## Integration with Researcher
The Library component works closely with the Researcher component, providing it with necessary reference materials and storing research outputs. See [Researcher documentation](./Researcher.md) for more details on this integration.
