from typing import Dict

import rio

from ..common import make_button, make_text
from ..researcher_model import ResearcherListModel, ResearcherModel



class ResearcherManagementComponentNames:
    """Component names used in the ResearcherManagement page."""

    HEADER = "header"
    RESEARCHER_LIST = "researcher_list"
    RESEARCHER_FORM = "researcher_form"
    RESEARCHER_DETAILS = "researcher_details"

    DISPLAY_ORDER = [
        HEADER,
        RESEARCHER_LIST,
        RESEARCHER_DETAILS,
    ]


@rio.page(
    name="Researcher Management",
    url_segment="researcher_management",
)
class ResearcherManagementPage(rio.Component):
    """Page for managing researchers in the system."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.researcher_list = ResearcherListModel()
        self.load_researchers()

        # Form state
        self.new_researcher_name = ""
        self.new_researcher_description = ""
        self.new_researcher_specialization = ""

        # Selected researcher
        self.selected_researcher_id = None

    def load_researchers(self):
        """Load researchers from the system."""
        # This would typically load from a database or API
        # For now, we'll create some sample researchers
        sample_researchers = [
            ResearcherModel(
                id=1,
                name="Document Analyst",
                description="Specializes in analyzing documents and extracting key information",
                specialization="Document Analysis"
            ),
            ResearcherModel(
                id=2,
                name="Data Synthesizer",
                description="Combines information from multiple sources to create comprehensive insights",
                specialization="Data Synthesis"
            ),
            ResearcherModel(
                id=3,
                name="Knowledge Navigator",
                description="Helps navigate complex knowledge bases and find relevant connections",
                specialization="Knowledge Navigation"
            )
        ]

        for researcher in sample_researchers:
            self.researcher_list.add_researcher(researcher)

    def create_researcher(self):
        """Create a new researcher."""
        if not self.new_researcher_name:
            return

        # Generate a new ID
        new_id = max([r.id or 0 for r in self.researcher_list.researchers], default=0) + 1

        # Create new researcher
        new_researcher = ResearcherModel(
            id=new_id,
            name=self.new_researcher_name,
            description=self.new_researcher_description,
            specialization=self.new_researcher_specialization if self.new_researcher_specialization else None
        )

        # Add to list
        self.researcher_list.add_researcher(new_researcher)

        # Clear form
        self.new_researcher_name = ""
        self.new_researcher_description = ""
        self.new_researcher_specialization = ""

        self.force_refresh()

    def delete_researcher(self, researcher_id: int):
        """Delete a researcher."""
        self.researcher_list.remove_researcher(researcher_id)
        if self.selected_researcher_id == researcher_id:
            self.selected_researcher_id = None
        self.force_refresh()

    def select_researcher(self, researcher_id: int):
        """Select a researcher for details view."""
        self.selected_researcher_id = researcher_id
        self.force_refresh()

    def _update_form_field(self, field_name: str, value: str):
        """Update a form field and refresh the UI."""
        setattr(self, field_name, value)
        self.force_refresh()

    def _build_researcher_item(self, researcher: ResearcherModel) -> rio.Component:
        """Build a list item for a researcher."""
        return rio.Container(
            rio.Row(
                rio.Column(
                    make_text(researcher.name, weight="bold"),
                    make_text(researcher.specialization or "General Research", size=14),
                    grow_x=True,
                ),
                make_button(
                    content="View",
                    on_press=lambda: self.select_researcher(researcher.id),
                    variant="outlined",
                ),
                make_button(
                    content="Delete",
                    on_press=lambda: self.delete_researcher(researcher.id),
                    variant="outlined",
                    color="error",
                ),
                grow_x=True,
                justify="space-between",
                align="center",
            ),
            padding=8,
            border_radius=4,
            background="#f9f9f9" if self.selected_researcher_id != researcher.id else "#e3f2fd",
            grow_x=True,
        )

    def _launch_researcher_interface(self, researcher: ResearcherModel):
        """Launch an interface to interact with this researcher."""
        # This would typically navigate to a chat interface with this researcher
        # For now we'll just update the UI to show this was clicked
        print(f"Launching researcher interface for: {researcher.name}")
        # Could use Rio navigation here to navigate to chat page with researcher context
        self.force_refresh()

    def _create_header_component(self) -> rio.Component:
        """Create the header component."""
        return make_text("Researcher Management", size=24, weight="bold")

    def _create_researcher_list_component(self) -> rio.Component:
        """Create the researcher list component."""
        researcher_items = [
            self._build_researcher_item(researcher)
            for researcher in self.researcher_list.researchers
        ]

        return rio.Container(
            rio.Column(
                make_text("Available Researchers"),
                *researcher_items,
                self._create_researcher_form_component(),
                spacing=2,
            ),
            grow_x=True,
        )

    def _create_researcher_form_component(self) -> rio.Component:
        """Build the form for creating a new researcher."""
        return rio.Column(
            make_text("Add New Researcher", weight="bold"),
            make_text(
                text=self.new_researcher_name,
                on_change=lambda v: self._update_form_field("new_researcher_name", v),
                label="Researcher Name",
                grow_x=True,
            ),
            make_text(
                text=self.new_researcher_description,
                on_change=lambda v: self._update_form_field("new_researcher_description", v),
                label="Researcher Description",
                grow_x=True,
            ),
            make_text(
                text=self.new_researcher_specialization,
                on_change=lambda v: self._update_form_field("new_researcher_specialization", v),
                label="Specialization (optional)",
                grow_x=True,
            ),
            make_button(
                content="Create Researcher",
                on_press=self.create_researcher,
                grow_x=True,
            ),
            spacing=2,
            grow_x=True,
        )

    def _create_researcher_details_component(self) -> rio.Component:
        """Create the researcher details component."""
        if not self.selected_researcher_id:
            return rio.Container(
                make_text("Select a researcher to view details"),
                grow_x=True,
            )

        researcher = self.researcher_list.get_researcher(
            self.selected_researcher_id
        )
        if not researcher:
            return rio.Container(
                make_text("Researcher not found"),
                grow_x=True,
            )

        return rio.Container(
            rio.Column(
                make_text(researcher.name, weight="bold"),
                make_text(f"Specialization: {researcher.specialization or 'General Research'}"),
                make_text("Description:", weight="bold"),
                make_text(researcher.description),
                make_button(
                    content="Launch Researcher Interface",
                    on_press=lambda: self._launch_researcher_interface(researcher),
                    variant="filled",
                    grow_x=True,
                ),
                spacing=2,
            ),
            grow_x=True,
        )

    def _generate_components(self) -> Dict[str, rio.Component]:
        """Generate all components used in the interface."""
        return {
            ResearcherManagementComponentNames.HEADER: self._create_header_component(),
            ResearcherManagementComponentNames.RESEARCHER_LIST: self._create_researcher_list_component(),
            ResearcherManagementComponentNames.RESEARCHER_DETAILS: self._create_researcher_details_component(),
        }

    def build(self) -> rio.Component:
        """Build the researcher management page."""
        components = self._generate_components()

        # Get the main components in order
        header = components[ResearcherManagementComponentNames.HEADER]

        # Create the main content row with list and details
        content_row = rio.Row(
            components[ResearcherManagementComponentNames.RESEARCHER_LIST],
            components[ResearcherManagementComponentNames.RESEARCHER_DETAILS],
            spacing=2,
            grow_x=True,
        )

        return rio.Column(
            header,
            content_row,
            grow_x=True,
            spacing=3,
        )
