# backend/ai-service/app/agents/data_retrieval.py
import httpx
from app.models.state import ConversationState
from app.config import settings
from app.cache import get_cache, set_cache
import hashlib
import json

async def data_retrieval_agent(state: ConversationState) -> ConversationState:
    """Retrieve data from rental or trade service API"""

    intent = state["intent"]
    optimized_query = state["optimized_query"]

    # Generate cache key
    cache_key = f"{intent}:{hashlib.md5(json.dumps(optimized_query, sort_keys=True).encode()).hexdigest()}"

    # Check cache
    if settings.AI_ENABLE_CACHE:
        cached_data = await get_cache(cache_key)
        if cached_data is not None:
            state["retrieved_data"] = cached_data
            state["metadata"]["cache_hit"] = True
            return state

    # Build API URL and params
    if intent == "rental":
        url = f"{settings.RENTAL_SERVICE_URL}/api/rental/list"
    else:
        url = f"{settings.TRADE_SERVICE_URL}/api/trade/list"

    # Convert optimized query to API params
    params = {}

    if "location" in optimized_query:
        # Use first location for now (could be enhanced to query all)
        locations = optimized_query["location"]
        if isinstance(locations, list) and len(locations) > 0:
            params["location"] = locations[0]
        else:
            params["location"] = locations

    if "min_price" in optimized_query:
        params["min_price"] = optimized_query["min_price"]
    if "max_price" in optimized_query:
        params["max_price"] = optimized_query["max_price"]

    if "type" in optimized_query:
        params["type"] = optimized_query["type"]

    if "category" in optimized_query:
        params["category"] = optimized_query["category"]
    if "condition" in optimized_query:
        params["condition"] = optimized_query["condition"]

    if "min_area" in optimized_query:
        params["min_area"] = optimized_query["min_area"]
    if "max_area" in optimized_query:
        params["max_area"] = optimized_query["max_area"]

    # Call API with retry logic
    max_retries = settings.AI_MAX_RETRIES
    timeout = settings.AI_TIMEOUT

    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=timeout)
                response.raise_for_status()
                data = response.json()

                retrieved_data = data.get("data", [])
                state["retrieved_data"] = retrieved_data
                state["metadata"]["cache_hit"] = False

                # Cache the result
                if settings.AI_ENABLE_CACHE:
                    await set_cache(cache_key, retrieved_data)

                return state

        except httpx.TimeoutException:
            if attempt == max_retries - 1:
                state["error"] = f"API timeout after {max_retries} retries"
                state["retrieved_data"] = []
        except httpx.HTTPError as e:
            if attempt == max_retries - 1:
                state["error"] = f"API error: {str(e)}"
                state["retrieved_data"] = []
        except Exception as e:
            state["error"] = f"Unexpected error: {str(e)}"
            state["retrieved_data"] = []
            break

    return state
