# Edit Log: Creation of Data Models

## Changes Made

- Created a new file `models/models.py` with three model classes:
  - `Library`: Represents a collection of resources with name, description, and public/private status
  - `User`: Represents application users with authentication information
  - `Researcher`: Extends user information for research-specific attributes

- Established relationships between models:
  - One-to-many relationship between Library and Users
  - One-to-one relationship between User and Researcher

- All models extend the `SchemaSpecificBaseModel` from `models/base.py` to maintain consistent schema configuration

## Architecture Impact

The new models provide the foundation for user management and resource organization within the application. The Library model will serve as a container for resources, while the User and Researcher models provide authentication and authorization capabilities.
