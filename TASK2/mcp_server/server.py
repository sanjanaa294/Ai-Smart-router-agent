import datetime
import re
from fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("My First MCP Server")


@mcp.tool()
def greet(name: str) -> str:
    """
    Greet a user by name.
    """
    return f"Hello, {name}! Welcome to MCP."


@mcp.tool()
def reverse_string(text: str) -> str:
    """
    Reverses the given input text string.
    """
    return f"Reversed: {text[::-1]}"


@mcp.tool()
def get_current_date() -> str:
    """
    Returns today's current date.
    """
    today = datetime.date.today().strftime("%B %d, %Y")
    return f"Today's date is {today}."


@mcp.tool()
def calculate(expression: str) -> str:
    """
    Evaluates a mathematical expression (e.g., '56 * 8' or '15 + 27').
    """
    try:
        # Extract mathematical digits and operators safely
        match = re.search(r"(\d+[\s\+\-\*\/\d]+)", expression)
        if match:
            expr = match.group(1).strip()
            result = eval(expr, {"__builtins__": None}, {})
            return f"Calculation result: {expr} = {result}"
        return f"Calculation result: {eval(expression, {'__builtins__': None}, {})}"
    except Exception as e:
        return f"Error evaluating expression '{expression}': {e}"


if __name__ == "__main__":
    mcp.run()