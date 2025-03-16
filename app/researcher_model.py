from pydantic import BaseModel
from typing import List, Optional


class ResearcherModel(BaseModel):
    """
    UI model representing a researcher.
    This is a simplified representation of the backend Researcher class
    for display and interaction in the UI.
    """
    id: Optional[int] = None
    name: str
    description: str
    specialization: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert the model to a dictionary representation for the UI."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "specialization": self.specialization or "General Research"
        }

    @staticmethod
    def from_dict(data: dict) -> 'ResearcherModel':
        """Create a researcher model from a dictionary."""
        return ResearcherModel(
            id=data.get("id"),
            name=data.get("name", ""),
            description=data.get("description", ""),
            specialization=data.get("specialization")
        )


class ResearcherListModel(BaseModel):
    """Model representing a list of researchers."""
    researchers: List[ResearcherModel] = []

    def add_researcher(self, researcher: ResearcherModel) -> None:
        """Add a researcher to the list."""
        self.researchers.append(researcher)

    def remove_researcher(self, researcher_id: int) -> None:
        """Remove a researcher from the list by ID."""
        self.researchers = [r for r in self.researchers if r.id != researcher_id]

    def get_researcher(self, researcher_id: int) -> Optional[ResearcherModel]:
        """Get a researcher by ID."""
        for researcher in self.researchers:
            if researcher.id == researcher_id:
                return researcher
        return None
