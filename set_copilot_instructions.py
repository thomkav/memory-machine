#!/usr/bin/env python3

import shutil

import inquirer
from rich.console import Console
from termcolor import colored

from constants import FilePaths

# Create a console instance
console = Console()


def get_instructions_dir():
    """Get the path to the instructions directory."""
    # Get the project root directory (assuming script is in scripts/ directory)
    instructions_dir = FilePaths.ROOT_DIR / ".github" / "instructions"

    # Ensure the directory exists
    if not instructions_dir.exists():
        console.print(
            f"Error: Instructions directory not found at {instructions_dir}",
            style="yellow",
        )
        console.print("Creating the directory...", style="blue")
        instructions_dir.mkdir(parents=True, exist_ok=True)

    return instructions_dir


def get_target_file():
    """Get the path to the target copilot-instructions.md file."""
    target_file = FilePaths.ROOT_DIR / ".github" / "copilot-instructions.md"

    # Ensure the .github directory exists
    if not target_file.parent.exists():
        target_file.parent.mkdir(parents=True, exist_ok=True)

    return target_file


def list_instruction_files():
    """List all available instruction files."""
    instructions_dir = get_instructions_dir()
    instruction_files = [f for f in instructions_dir.glob("*.md") if f.is_file()]

    if not instruction_files:
        console.print(
            "No instruction files found in .github/instructions/", style="yellow"
        )
        console.print("Please create an instruction file first.", style="yellow")
        return []

    return sorted(instruction_files)


def display_instruction_files(files):
    """Display the available instruction files with indices."""
    if not files:
        return

    console.print("\nAvailable instruction files:", style="cyan bold")
    for idx, file_path in enumerate(files, 1):
        console.print(f"[green]{idx}.[/green] {file_path.name}")
    console.print()


def reset_contextual_files():
    file_visibility_log = FilePaths.COPILOT_FILE_VISIBILITY_LOG
    # Set the contents of the file to an empty string
    file_visibility_log.write_text("")
    console.print("✓ Reset file visibility log", style="green")


def switch_instructions(selection=None):
    """Switch to the selected instruction file."""
    instruction_files = list_instruction_files()

    if not instruction_files:
        return False

    # Use the selection parameter if provided, otherwise prompt the user
    if selection is None:
        display_instruction_files(instruction_files)
        # Create a list of instruction file choices with their names

        choices = [f"{f.name}" for f in instruction_files]

        # Use inquirer to create an interactive selection prompt
        questions = [
            inquirer.List(
                "instruction",
                message=colored("Select the instruction set to use:", "cyan"),
                choices=choices,
                carousel=True,
            )
        ]

        try:
            answers = inquirer.prompt(questions)
            if not answers:  # User pressed Ctrl+C or similar
                console.print("Operation cancelled.", style="yellow")
                return False

            # Find the selected file by name
            selected_file_name = answers["instruction"]
            selected_file = next(
                f for f in instruction_files if f.name == selected_file_name
            )
        except Exception as e:
            console.print(f"Error during selection: {e}", style="red")
            return False
    else:
        # If a numeric selection was provided via command line
        display_instruction_files(instruction_files)

        # Validate the selection
        if not (1 <= selection <= len(instruction_files)):
            console.print(
                f"Invalid selection. Please choose a number between 1 and {len(instruction_files)}.",
                style="red",
            )
            return False

        selected_file = instruction_files[selection - 1]

    target_file = get_target_file()

    # Copy the selected file to the target location
    try:
        shutil.copy2(selected_file, target_file)
        console.print(
            f"✓ Success! [bold]Switched to '[cyan]{selected_file.name}[/cyan]'[/bold]"
        )
        console.print(
            f"  Instructions updated at: [white]{str(target_file)}[/white]",
            style="green",
        )
        return True
    except Exception as e:
        console.print(f"Error switching instructions: {e}", style="red")
        return False


def create_sample_instruction(name=None):
    """Create a sample instruction file if none exist."""
    instructions_dir = get_instructions_dir()

    if name is None:
        # Use inquirer to get the name
        questions = [
            inquirer.Text(
                "name",
                message=colored("Enter a name for the instruction file:", "cyan"),
                default="default-instructions",
            )
        ]
        answers = inquirer.prompt(questions)
        if not answers:  # User pressed Ctrl+C or similar
            console.print("Operation cancelled.", style="yellow")
            return
        name = answers["name"]

    # Ensure name ends with .md
    if not name.endswith(".md"):
        name += ".md"

    file_path = instructions_dir / name

    # Don't overwrite existing file
    if file_path.exists():
        console.print(
            f"File '{name}' already exists. Skipping sample creation.", style="yellow"
        )
        return

    sample_content = """# Copilot Instructions

This is a sample instruction file for GitHub Copilot.

## Guidelines
- Write clean, well-documented code
- Follow project style guidelines
- Explain your approach when appropriate
- Include error handling
"""

    with open(file_path, "w") as f:
        f.write(sample_content)

    console.print(f"✓ Created: [cyan]{file_path}[/cyan]", style="green bold")


def main():
    """Run the main interactive menu for Copilot instruction management."""
    console.print("\n╔══════════════════════════════════════╗", style="cyan")
    console.print(
        "║ [bold white]Copilot Instruction Switcher[/bold white] ║", style="cyan"
    )
    console.print("╚══════════════════════════════════════╝\n", style="cyan")

    while True:
        # Define the main menu options
        menu_choices = [
            "List available instruction files",
            "Switch instruction file",
            "Create new instruction file",
            "Reset contextual files",
            "Exit",
        ]

        questions = [
            inquirer.List(
                "action",
                message=colored("What would you like to do?", "cyan"),
                choices=menu_choices,
                carousel=True,
            )
        ]

        answers = inquirer.prompt(questions)
        if not answers:  # User pressed Ctrl+C or similar
            console.print("Operation cancelled.", style="yellow")
            break

        choice = answers["action"]

        if choice == "List available instruction files":
            instruction_files = list_instruction_files()
            if instruction_files:
                display_instruction_files(instruction_files)
            console.print("Press Enter to continue...", style="cyan")
            input()

        elif choice == "Switch instruction file":
            switch_instructions()
            console.print("Press Enter to continue...", style="cyan")
            input()

        elif choice == "Create new instruction file":
            create_sample_instruction()
            console.print("Press Enter to continue...", style="cyan")
            input()

        elif choice == "Reset contextual files":
            reset_contextual_files()
            console.print("Press Enter to continue...", style="cyan")
            input()

        elif choice == "Exit":
            console.print("Goodbye!", style="cyan bold")
            break


if __name__ == "__main__":
    main()
