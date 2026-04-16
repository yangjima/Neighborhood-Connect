from app.models.state import ConversationState
import json
import os

# Load synonyms dictionary
synonyms_path = os.path.join(os.path.dirname(__file__), "synonyms.json")
with open(synonyms_path, "r", encoding="utf-8") as f:
    SYNONYMS = json.load(f)

async def query_optimizer_agent(state: ConversationState) -> ConversationState:
    """Optimize query conditions with synonyms and expansions"""

    params = state["extracted_params"]
    optimized = {}
    intent = state["intent"]

    # Location expansion
    if "location" in params:
        location = params["location"]
        expanded_locations = SYNONYMS["locations"].get(location, [location])
        optimized["location"] = expanded_locations

    # Price range (already optimized by parameter extractor)
    if "min_price" in params:
        optimized["min_price"] = params["min_price"]
    if "max_price" in params:
        optimized["max_price"] = params["max_price"]

    # Area range
    if "min_area" in params:
        optimized["min_area"] = params["min_area"]
    if "max_area" in params:
        optimized["max_area"] = params["max_area"]

    # Rental type
    if "type" in params:
        rental_type = params["type"]
        optimized["type"] = rental_type

    # Trade category with keyword expansion
    if "category" in params:
        category = params["category"]
        optimized["category"] = category

        # Extract keywords from query for synonym matching
        query_lower = state["user_query"].lower()
        keywords = []

        for item, synonyms in SYNONYMS.get(category, {}).items():
            if item in query_lower:
                keywords.extend(synonyms)

        if keywords:
            optimized["keywords"] = keywords

    # Condition
    if "condition" in params:
        optimized["condition"] = params["condition"]

    # Facilities
    if "facilities" in params:
        optimized["facilities"] = params["facilities"]

    state["optimized_query"] = optimized

    return state
