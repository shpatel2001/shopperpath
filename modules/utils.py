import pandas as pd

def safe_get(row, key, default=""):
    """Safely get a value from a DataFrame row."""
    return row[key] if key in row and pd.notna(row[key]) else default


def format_json_output(text: str) -> str:
    """Ensures AI output is displayed cleanly in Streamlit."""
    try:
        import json
        parsed = json.loads(text)
        return json.dumps(parsed, indent=2)
    except:
        # If it's not valid JSON, return raw text
        return text