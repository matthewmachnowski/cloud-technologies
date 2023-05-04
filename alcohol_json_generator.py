from typing import Dict, List
import json
import pandas as pd
from collections import defaultdict


DISTILLED_ALCOHOLS = [
    "brandy",
    "cognac",
    "gin",
    "mezcal",
    "rum",
    "tequila",
    "vodka",
    "whisky",
    'liqueur'
]

FERMENTED_ALCOHOLS = [
    "beer",
    "cider",
    "sake",
    "wine",
]

def get_alcohol_category(alcohol_type: str) -> str:
    """Determine the category of the given alcohol_type."""
    if alcohol_type.lower() in DISTILLED_ALCOHOLS:
        return "distilled"
    elif alcohol_type.lower() in FERMENTED_ALCOHOLS:
        return "fermented"
    else:
        return ""


def create_json_dict(csv_file: str, keywords_file: str) -> List[Dict]:
    """Create a JSON dictionary from the given CSV file and keywords JSON file."""
    # Load keywords from the provided JSON file
    with open(keywords_file) as f:
        keywords_dict = json.load(f)

    # Load alcohol brands and types from the provided CSV file
    df = pd.read_csv(csv_file)

    # Initialize alcohol_dict with defaultdict for simplified dictionary creation
    alcohol_dict = {
        "distilled": defaultdict(lambda: {"name": "", "keywords": [], "brands": []}),
        "fermented": defaultdict(lambda: {"name": "", "keywords": [], "brands": []}),
    }

    # Iterate through each row in the DataFrame and populate alcohol_dict
    for _, row in df.iterrows():
        brand = row["Brand"]
        alcohol_type = row["Type"]

        # Check if both alcohol type and brand are present
        if pd.isna(alcohol_type) or pd.isna(brand):
            print(f"Skipping row due to missing alcohol type or brand: {row}")
            continue

        # Get the alcohol category (distilled or fermented) or continue if unknown
        category = get_alcohol_category(alcohol_type)
        if not category:
            print(f"Unknown alcohol type: {alcohol_type}, for brand {brand}")
            continue

        # Get or create the type_dict for the specific alcohol type in the category
        type_dict = alcohol_dict[category][alcohol_type.lower()]
        type_dict["name"] = alcohol_type.lower()
        type_dict["keywords"] = keywords_dict[category].get(alcohol_type.lower(), [])
        type_dict["brands"].append(brand)

    # Create the final alcohol_list by converting the defaultdict values to lists
    alcohol_list = [
        {
            "name": category,
            "keywords": keywords_dict[category].get("general", []),
            "children": list(alcohol_dict[category].values()),
        }
        for category in ["distilled", "fermented"]
    ]

    return alcohol_list


def save_json(json_dict: List[Dict], file_path: str) -> None:
    """Save the provided JSON dictionary to a file with the given file_path."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(json_dict, f, ensure_ascii=False, indent=4)


def main() -> None:
    """Main function for the script."""
    # Define input and output file paths
    keywords_file = 'keywords.json'
    csv_file = 'alcohols.csv'

    # Create the JSON dictionary using the provided input files
    json_dict = create_json_dict(csv_file, keywords_file)

    # Save the JSON dictionary to a file
    json_file = 'alcohols.json'
    save_json(json_dict, json_file)


if __name__ == '__main__':
    main()
