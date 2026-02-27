import pandas as pd

REQUIRED_COLUMNS = [
    "item_name",
    "category",
    "brand",
    "dietary_tags",
    "customer_notes",
    "historical_stock_risk",
    "historical_substitution_rate"
]

def validate_and_clean(df: pd.DataFrame) -> pd.DataFrame:
    # Ensure required columns exist
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Fill empty text fields
    text_fields = ["dietary_tags", "customer_notes", "brand"]
    for col in text_fields:
        df[col] = df[col].fillna("")

    # Fill numeric fields
    numeric_fields = ["historical_stock_risk", "historical_substitution_rate"]
    for col in numeric_fields:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df