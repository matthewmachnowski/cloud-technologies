import json
import os
import requests
from typing import List, Tuple, Optional

# Function that builds a query with a drink name and mode ('c' or 'm')
def build_query(drink_name: str, mode: str = "c") -> dict:
    drink_name = drink_name.replace("'", "-").replace(":", "-")
    words = drink_name.split(" ")
    required = [{"keyword": word, "mode": mode} for word in words]
    return {"required": required}

# Function that sends a POST request and returns the response as a dictionary
def send_post_request(session: requests.Session, url: str, query: dict) -> dict:
    return session.post(url, json=query).json()

# Function that saves data to a JSON file
def save_to_json_file(data: dict, filepath: str) -> None:
    os.makedirs('output', exist_ok=True)
    with open(os.path.join('output', filepath), 'w') as f:
        json.dump(data, f, indent=4)

# Function that adds optional keywords to a query
def add_optional_keywords(query: dict, optional_keywords: List[str], mode: str = "c", optional_threshold: int = 1) -> dict:
    query.update({
        "optional": [{"keyword": keyword, "mode": mode} for keyword in optional_keywords],
        "optionalThreshold": optional_threshold
    })
    return query

# Function that tests a query in the estimator and returns the result and response
def test_query_in_estimator(session: requests.Session, query: dict, url: str, brand_name: str, mode: str = None, optional_threshold: int = None) -> Tuple[bool, dict]:
    result = send_post_request(session, url, query)
    total_quantity = sum(result['sources'][s]["quantity"] for s in result['sources'])
    
    mode_info = f"for {mode}" if mode else ""
    optional_threshold_info = f"and optionalThreshold ({optional_threshold})" if optional_threshold else ""

    print(f"{brand_name}{' was NOT found!' if total_quantity == 0 else f' was found! Total quantity'} {mode_info} {optional_threshold_info}: {total_quantity}")

    if total_quantity > 0:
        save_to_json_file(result, f"{brand_name}.json")
        return total_quantity > 0, result
    return None

# Function that processes a query for a given brand and drink type
def process_brand(session: requests.Session, url: str, brand: str, drink_type: str, type_keywords: List[str], category_keywords: List[str]) -> dict:
    functions_list = [query_step1, query_step2, query_step3]  # Add more steps as needed

    # Create dictionaries of arguments for each function
    args_step1_2 = {
        "session": session,
        "url": url,
        "brand": brand,
    }

    args_step3_4 = {
        "session": session,
        "url": url,
        "brand": brand,
        "type_keywords": type_keywords,
        "category_keywords": category_keywords,
    }
   
    last_good_query = None
    response = None
    step3_or_later = False

    for i, func in enumerate(functions_list):
        # Choose the appropriate arguments for each function
        if i < 2:
            func_args = args_step1_2
        else:
            # Add the brand's keywords to the category keywords
            func_args = args_step3_4
        func_args["step"] = i + 1

        result, response, step3_or_later_current = func(**func_args)

        # If the response is "false_response", stop processing and break the loop
        if response == "false_response":
            break

        if response == "response":
            last_good_query = result
            if step3_or_later_current:
                step3_or_later = True

    if last_good_query:
        return last_good_query, step3_or_later
    else:
        return None, False

# Function that builds and tests a query in mode "c"
def query_step1(session: requests.Session, url: str, brand: str, step: int) -> Tuple[dict, str, bool]:
    query = build_query(brand)
    result = test_query_in_estimator(session, query, url, brand, mode="c")

    # Return the query, the response, and a boolean indicating whether step 3 or later has been reached
    return ({"id": brand, "required": query["required"]}, "false_response" if not result else "response", step >= 3)

# Function that builds and tests a query in mode "m"
def query_step2(session: requests.Session, url: str, brand: str, step: int) -> Tuple[dict, str, bool]:
    query_m = build_query(brand, mode="m")
    result_m = test_query_in_estimator(session, query_m, url, brand, mode="m")

    # Return the query, the response, and a boolean indicating whether step 3 or later has been reached
    return ({"id": brand, "required": query_m["required"]}, "false_response" if not result_m else "response", step >= 3)

# Function that builds and tests a query in mode "m" with optional keywords
def query_step3(session: requests.Session, url: str, brand: str, type_keywords: List[str], category_keywords: List[str], step: int) -> Tuple[Optional[dict], str, bool]:
    # Build the query with mode "m"
    query_m = build_query(brand, mode="m")
    query_optional_m = add_optional_keywords(query_m, category_keywords, mode="m")
    optional_threshold = query_optional_m["optionalThreshold"]

    # Test the query with optional keywords using mode "m"
    result_opt_m = test_query_in_estimator(session, query_optional_m, url, brand, mode="m", optional_threshold=optional_threshold)

    # Keep track of the last successful query
    last_good_query = None

    # Keep track of the last successful query with more than one optional keyword
    last_successful_query = None

    # Try to get more results by increasing the optional threshold
    while result_opt_m:
        last_good_query = query_optional_m.copy()
        optional_threshold += 1
        query_optional_m["optionalThreshold"] = optional_threshold
        result_opt_m = test_query_in_estimator(session, query_optional_m, url, brand, mode="m", optional_threshold=optional_threshold)

    # If the last query did not yield any results, remove optional keywords from the end
    if not result_opt_m and last_good_query:
        last_successful_query = last_good_query.copy()

        if len(last_good_query["optional"]) == 1:
            last_successful_query = last_good_query.copy()
        else:
            while len(last_good_query["optional"]) > 1:
                last_good_query["optional"] = last_good_query["optional"][:-1]
                result_opt_m = test_query_in_estimator(session, last_good_query, url, brand, mode="m", optional_threshold=last_good_query["optionalThreshold"])

                if not result_opt_m:
                    break
                else: 
                    last_successful_query = last_good_query.copy()

    # If a successful query with optional keywords was found, return it along with the response and a boolean indicating whether step 3 or later has been reached
    if last_successful_query:
        return (
            {
                "id": brand,
                "required": last_successful_query["required"],
                "optional": last_successful_query["optional"],
                "optionalThreshold": last_successful_query["optionalThreshold"]
            }, "response", step >= 3
        )
    # If no successful query with optional keywords was found, return None and the response
    else:
        return None, "false_response", False

def process_recursive(session: requests.Session, url: str, node: dict, category_keywords: List[str], all_queries: List[dict]) -> None:
    # If the node contains brands, process each brand
    if "brands" in node:
        for brand in node["brands"]:
            query, step3_or_later = process_brand(session, url, brand, node["name"], node["keywords"], category_keywords)
            if query and step3_or_later:
                all_queries.append(query)
    # If the node contains children, process each child recursively
    else:
        for child in node["children"]:
            child_category_keywords = category_keywords.copy()
            if not category_keywords:  # Only add general keywords if processing a root category
                child_category_keywords += node["keywords"]
            child_category_keywords += child["keywords"]
        
            process_recursive(session, url, child, child_category_keywords, all_queries)

def main() -> None:
    # Create the "output" directory if it doesn't exist
    if os.path.exists("output"):
        for filename in os.listdir("output"):
            os.remove(os.path.join("output", filename))
    else:
        os.makedirs("output")

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
