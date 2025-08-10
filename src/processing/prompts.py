from src.models.knowledge_level import KnowledgeLevel


def build_prompt(abstract: str, level: KnowledgeLevel) -> str:
    """
    Build a summarization prompt tailored to the user's knowledge level.

    Args:
        abstract: The abstract text of the research paper.
        level: Target knowledge level for the summary.

    Returns:
        The formatted prompt string for the summarization model.

    Raises:
        ValueError: If the provided knowledge level is not supported.
    """
    instructions = {
        KnowledgeLevel.GENERAL: (
            "Summarize this research paper in plain language for a general audience. "
            "Avoid technical jargon and focus on the main idea and why it matters."
        ),
        KnowledgeLevel.UNDERGRADUATE: (
            "Summarize this research paper for a university student with basic technical knowledge. "
            "Explain key concepts clearly and provide some context."
        ),
        KnowledgeLevel.RESEARCHER: (
            "Summarize this research paper for a professional or researcher in the field. "
            "Include technical details, key findings, limitations, implications as well as other technical remarks that are relevant."
        ),
    }

    if level not in instructions:
        raise ValueError(f"Unsupported knowledge level: {level}")

    return f"{instructions[level]}\n\nAbstract:\n{abstract}"