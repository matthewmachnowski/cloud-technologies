from typing import Dict, List, Union
import json
import pandas as pd


def create_json_dict(excel_file: str, keywords_file: str) -> List[Dict]:
    # Load keywords from the provided JSON file
    with open(keywords_file) as f:
        keywords_dict = json.load(f)

    # Create a dictionary with alcohol categories and brands based on the provided Excel file
    df = pd.read_excel(excel_file)
    alcohol_list = [
        {
            "name": "distilled",
            "keywords": keywords_dict["distilled"].get("general", []),
            "children": [],
        },
        {
            "name": "fermented",
            "keywords": keywords_dict["fermented"].get("general", []),
            "children": [],
        },
    ]

    alcohol_dict = {
        "distilled": alcohol_list[0]["children"],
        "fermented": alcohol_list[1]["children"],
    }

    for _, row in df.iterrows():
        brand = row["Brand"]
        alcohol_type = row["Type"]

        if alcohol_type.lower() in [
            "brandy",
            "cognac",
            "gin",
            "mezcal",
            "rum",
            "tequila",
            "vodka",
            "whisky",
        ]:
            category = "distilled"
        elif alcohol_type.lower() in ["beer", "cider", "sake", "wine"]:
            category = "fermented"
        else:
            print(f"Unknown alcohol type: {alcohol_type}")
            continue

        # Find the existing dictionary for the alcohol type, or create a new one
        type_dict = next(
            (
                d
                for d in alcohol_dict[category]
                if d["name"].lower() == alcohol_type.lower()
            ),
            None,
        )
        if type_dict is None:
            brand_keywords = keywords_dict[category].get(
                alcohol_type.lower(), []
            )  # Get keywords for the type of alcohol
            type_dict = {
                "name": alcohol_type.lower(),
                "keywords": brand_keywords,
                "brands": [],
            }
            alcohol_dict[category].append(type_dict)

        # Appending the brand name to the list of alcohol types for the corresponding category
        type_dict["brands"].append(brand)

    return alcohol_list




def save_json(json_dict: Dict, file_path: str) -> None: 
    # Save the provided dictionary as a JSON file.
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(json_dict, f, ensure_ascii=False, indent=4)


def main() -> None:
    keywords_file = 'keywords.json'
    excel_file = 'alcohols.xlsx'
    json_dict = create_json_dict(excel_file, keywords_file)
    json_file = 'alcohols.json'
    save_json(json_dict, json_file)


if __name__ == '__main__':
    main()
