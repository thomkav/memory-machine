from pydantic import BaseModel

from .document import Doc


class Context(BaseModel):
    """Schema for the context passed to the agent."""

    documents: list[Doc] = []


class InstructionNames(str):
    """Enumeration of instructions for the agent."""

    LAZY = "lazy"
    SUMMARIZE_DOCUMENT = "summarize_document"


def generate_instructions(
    instruction_name: str,
    context: Context,
) -> str:
    """
    Generate instructions for the agent based on the provided context.
    """

    if instruction_name == InstructionNames.LAZY:
        instructions = "Do nothing. Just return the context you received."
        instructions += "\n\nContext:\n" + str(context)

    elif instruction_name == InstructionNames.SUMMARIZE_DOCUMENT:

        document = context.documents[0].content.strip()

        instructions = f"""
        You are a document summarizer. Your task is to summarize the document
        provided in the context below. It will be a string of text.
        If no document is provided, return 'No document provided.' and report what context you received.
        You should not include any other information in your response.

        The document is as follows:
        <context>
        {document}
        </context>
        """

    else:
        raise ValueError(f"Unknown instruction name: {instruction_name}")

    return instructions.strip()
