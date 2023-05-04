import json
import os
import re
import requests
from typing import List, Tuple, Optional


def build_query(drink_name: str, mode: str = "c") -> dict:
    """Build a query with a drink name and mode ('c' or 'm')."""
    # Replace certain characters in the drink name
    translation_table = str.maketrans({"'": "-", ":": "-",".": "-"})
    drink_name = drink_name.translate(translation_table)
    # Split the drink name into words
    words = drink_name.split(" ")
    # Return a dictionary with the required keywords and their mode
    return {"required": [{"keyword": word, "mode": mode} for word in words]}


def send_post_request(session: requests.Session, url: str, query: dict) -> dict:
    """Send a POST request and return the response as a dictionary."""
    return session.post(url, json=query).json()


def save_to_json_file(data: dict, filepath: str) -> None:
    """Save data to a JSON file - output folder"""
    # Create the 'output' directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    # Save the data to a JSON file in the 'output' directory
    with open(os.path.join('output', filepath), 'w') as f:
        json.dump(data, f, indent=4)


def add_optional_keywords(query: dict, optional_keywords: List[str], mode: str = "m", optional_threshold: int = 1) -> dict:
    """Add optional keywords to a query."""
    # Update the query with optional keywords, their mode, and the optional threshold
    query.update({
        "optional": [{"keyword": keyword, "mode": mode} for keyword in optional_keywords],
        "optionalThreshold": optional_threshold
    })
    return query


def test_query_in_estimator(session: requests.Session, query: dict, url: str, brand_name: str, mode: str, optional_threshold: int = None) -> Tuple[bool, dict]:
    """Test a query in the estimator and return the result and response."""
    # Send the post request with the given query and get the response as a dictionary
    result = send_post_request(session, url, query)
    # Calculate the total quantity by summing up the quantities of all sources - URLs 
    total_quantity = sum(result['sources'][s]["quantity"] for s in result['sources'])

    # Prepare additional information for the output message
    mode_info = f"for mode ({mode})" if mode else ""
    optional_threshold_info = f"and optionalThreshold ({optional_threshold})" if optional_threshold else ""

    print(f"{brand_name}{' was NOT found!' if total_quantity == 0 else f' was found! Total quantity'} {mode_info} {optional_threshold_info}: {total_quantity}")

    # If the total quantity is greater than 0 and optional keywords are present in the query, save the result to a JSON file
    if total_quantity > 0 and "optional" in query:
        save_to_json_file(result, f"{brand_name}.json")
        
    # If the total quantity is greater than 0, return the tuple (True, result)
    if total_quantity > 0:
        return total_quantity > 0, result
    return None


# Analyze URLs and find the exact optional keywords present in them
def analyze_urls(urls: List[str], optional_keywords: List[str]) -> List[str]:
    found_keywords = set()
    for url in urls:
        for keyword in optional_keywords:
            if re.search(r'\b' + re.escape(str(keyword)) + r'\b', str(url), re.IGNORECASE):
                found_keywords.add(keyword)
    return list(found_keywords)
    

def modify_optional_keywords(session: requests.Session, url: str, brand: str, query_optional_m: dict) -> Optional[dict]:
    """Modify the optional keywords in the query by increasing the optional threshold and removing optional keywordsto find the last successful query."""
    # Increase optional threshold and test the query
    result_opt_m = test_query_in_estimator(session, query_optional_m, url, brand, mode="m", optional_threshold=query_optional_m["optionalThreshold"])
    last_good_query = None

    all_urls = []  # Initialize a list to store all the URLs

    # Keep increasing the optional threshold until the query is no longer successful
    while result_opt_m:
        last_good_query = query_optional_m.copy()
        all_urls.extend(result_opt_m[1]['sources'][s]['urls'] for s in result_opt_m[1]['sources'])  # Collect URLs
        query_optional_m["optionalThreshold"] += 1
        result_opt_m = test_query_in_estimator(session, query_optional_m, url, brand, mode="m", optional_threshold=query_optional_m["optionalThreshold"])
    
    # Update the last_good_query with the exact optional keywords
    if last_good_query:
        exact_optional_keywords = analyze_urls(all_urls, [k["keyword"] for k in last_good_query["optional"]])
        last_good_query["optional"] = [{"keyword": keyword, "mode": "m"} for keyword in exact_optional_keywords]

    return last_good_query


def build_and_test_queries(session: requests.Session, url: str, brand: str, category_keywords: List[str]) -> Tuple[Optional[dict], bool]:
    """Build and test queries for the given brand in modes 'c' and 'm', with optional keywords and thresholds."""
    step3_or_later = False
    last_good_query = None

    # Test queries in modes 'c' and 'm'
    for step in [0, 1]:
        mode = "c" if step == 0 else "m"
        query = build_query(brand, mode=mode)
        result = test_query_in_estimator(session, query, url, brand, mode=mode)

        # If the query is successful, store it as the last good query
        if result:
            last_good_query = {"id": brand, "required": query["required"]}
        else:
            break

    if last_good_query and last_good_query["required"][0]["mode"] == "m":
        # Test query in mode 'm' with optional keywords and thresholds
        query_optional_m = add_optional_keywords(query, category_keywords, mode)
        last_successful_query = modify_optional_keywords(session, url, brand, query_optional_m)

        # If the modified query is successful, update the last good query with optional keywords and thresholds
        if last_successful_query:
            last_good_query = {
                "id": brand,
                "required": last_successful_query["required"],
                "optional": last_successful_query["optional"],
                "optionalThreshold": last_successful_query["optionalThreshold"]
            }
            step3_or_later = True

    return last_good_query, step3_or_later


def process_brand(session: requests.Session, url: str, brand: str, category_keywords: List[str]) -> Tuple[Optional[dict], bool]:
    """Process a brand by building and testing queries, and return the last good query and a flag indicating the query's complexity."""
    last_good_query, step3_or_later = build_and_test_queries(session, url, brand, category_keywords)

    # If a last good query is found, return it along with the step3_or_later flag
    if last_good_query:
        return last_good_query, step3_or_later
    else:
        return None, False


def process_recursive(session: requests.Session, url: str, node: dict, category_keywords: List[str], all_queries: List[dict]) -> None:
    """Process a node recursively, updating the list of queries."""
    # If the node contains brands, process each brand
    if "brands" in node:
        for brand in node["brands"]:
            query, step3_or_later = process_brand(session, url, brand, category_keywords)
            # Add the query to the list of all queries if it uses optional keywords and thresholds
            if query and step3_or_later:
                all_queries.append(query)
    # If the node contains children, process each child recursively
    else:
        for child in node["children"]:
            # Create a copy of the current category keywords to avoid modifying the original list
            child_category_keywords = category_keywords.copy()
            
            # Only add general keywords if processing a root category
            if not category_keywords:
                child_category_keywords += node["keywords"]

            # Add child-specific keywords to the list
            child_category_keywords += child["keywords"]
            
            # Recursively process the child node with the updated category keywords
            process_recursive(session, url, child, child_category_keywords, all_queries)


def main() -> None:
    """Main function to run the script."""
    # Ensure the "output" directory exists and is empty
    os.makedirs("output", exist_ok=True)
    for filename in os.listdir("output"):
        os.remove(os.path.join("output", filename))

    # Open the "alcohols.json" file and parse it
    with open("alcohols.json") as f:
        alcohols = json.load(f) 

    # Paste adress URL to estimator 	
    url = ""

    # Create a new requests session and an empty list of queries
    with requests.Session() as session:
        all_queries = []

        # Process each alcohol category
        for category in alcohols:
            process_recursive(session, url, category, category["keywords"], all_queries)

    # Save the list of queries to a file
    with open("queries.json", "w") as f:
        json.dump({"results": all_queries}, f, indent=4)


if __name__ == '__main__':
    main()
