"""
utils.py
--------
Utility helper functions for formatting text and printing responses.
"""

def clean_text(text: str) -> str:
    """Cleans and normalizes input text."""
    if not text:
        return ""
    return text.strip().lower()


def format_response(route: str, tool_name: str, answer: str) -> str:
    """Formats response for terminal output."""
    banner = "-" * 50
    return (
        f"\nRouter Selected:\n{route}\n\n"
        f"Tool Invoked:\n{tool_name}\n\n"
        f"Answer:\n{answer}\n"
        f"{banner}\n"
    )
