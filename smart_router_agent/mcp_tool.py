"""
mcp_tool.py - Model Context Protocol (MCP) tool execution engine.
Performs dynamic actions: greetings, date queries, math calculations, and string reversal.
"""
import datetime
import re
from utils import clean_text


def mcp_greet(question: str) -> str:
    cleaned = clean_text(question)
    match = re.search(r"greet\s+([a-zA-Z]+)", cleaned)
    name = match.group(1).capitalize() if match else "there"
    return f"[MCP Tool: Greet] Hello {name}! Welcome to Smart Query Router Agent."


def mcp_date() -> str:
    today = datetime.date.today().strftime("%B %d, %Y")
    return f"[MCP Tool: Date] Today's date is {today}."


def mcp_calculate(question: str) -> str:
    match = re.search(r"(\d+[\s\+\-\*\/\d]+)", question)
    if match:
        expr = match.group(1).strip()
        try:
            result = eval(expr, {"__builtins__": None}, {})
            return f"[MCP Tool: Calculator] Calculation result: {expr} = {result}"
        except Exception as e:
            return f"[MCP Tool: Calculator] Error evaluating '{expr}': {e}"
    return "[MCP Tool: Calculator] Please provide a valid arithmetic expression."


def mcp_reverse(question: str) -> str:
    cleaned = clean_text(question)
    target = question
    if "reverse" in cleaned:
        parts = question.split("reverse", 1)
        if len(parts) > 1 and parts[1].strip():
            target = parts[1].strip()
            target = re.sub(r"^(this|the)?\s*string\s*", "", target, flags=re.IGNORECASE).strip() or question
    return f"[MCP Tool: String Reverser] Original: '{target}' -> Reversed: '{target[::-1]}'"


def execute_mcp_tool(question: str) -> str:
    """Routes prompt to specific action function based on keyword."""
    cleaned_q = clean_text(question)
    if "greet" in cleaned_q:
        return mcp_greet(question)
    elif "date" in cleaned_q:
        return mcp_date()
    elif "calculate" in cleaned_q or any(op in cleaned_q for op in ['+', '*', '/']):
        return mcp_calculate(question)
    elif "reverse" in cleaned_q:
        return mcp_reverse(question)
    return f"[MCP Tool: Generic] Executed action for: '{question}'"
