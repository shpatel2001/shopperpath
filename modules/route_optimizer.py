import pandas as pd

# Convert aisle labels into sortable numeric values
def normalize_aisle(aisle):
    if isinstance(aisle, str):
        aisle = aisle.strip()

        # Produce section comes first
        if aisle.lower() == "produce":
            return 0

        # Aisles like "A5", "A10"
        if aisle.startswith("A"):
            try:
                return int(aisle[1:])
            except:
                return 999  # fallback for unexpected formats

    return 999


# Estimate time spent in each aisle based on number of items
def estimate_time(num_items):
    if num_items <= 2:
        return 1
    elif num_items <= 5:
        return 2
    else:
        return 3


# Main route optimizer function
def generate_route(df):
    df = df.copy()

    # Normalize aisle values
    df["aisle_num"] = df["aisle"].apply(normalize_aisle)

    # Sort by aisle order
    df_sorted = df.sort_values(by="aisle_num")

    # Group items by aisle
    grouped = df_sorted.groupby("aisle")

    route = []
    total_time = 0

    for aisle, items in grouped:
        num_items = len(items)
        time_needed = estimate_time(num_items)
        total_time += time_needed

        route.append({
            "aisle": aisle,
            "items": items["item_name"].tolist(),
            "num_items": num_items,
            "time_estimate": time_needed
        })

    return route, total_time