from typing import Dict, Any, List
from app.models.state import ConversationState

async def response_formatter_agent(state: ConversationState) -> ConversationState:
    """
    Format retrieved data into frontend-friendly JSON response.

    Generates query understanding text and provides suggestions when no results found.
    """
    # Check for errors first
    if state.get("error"):
        state["formatted_response"] = {
            "success": False,
            "error": state["error"],
            "data": [],
            "total": 0
        }
        return state

    # Get retrieved data
    retrieved_data = state.get("retrieved_data", [])
    extracted_params = state.get("extracted_params", {})

    # Generate query understanding text
    query_understanding = _generate_understanding(extracted_params, state["intent"])

    # Build response
    formatted_response = {
        "success": True,
        "data": retrieved_data,
        "total": len(retrieved_data),
        "query_understanding": query_understanding,
        "applied_filters": extracted_params
    }

    # Add suggestions if no results
    if len(retrieved_data) == 0:
        formatted_response["suggestions"] = _generate_suggestions(extracted_params, state["intent"])

    state["formatted_response"] = formatted_response
    return state

def _generate_understanding(params: Dict[str, Any], intent: str) -> str:
    """Generate human-readable query understanding text"""
    parts = []

    if params.get("location"):
        location = params["location"]
        if isinstance(location, list):
            location = location[0]
        parts.append(f"{location}地区")

    if params.get("min_price") and params.get("max_price"):
        parts.append(f"{params['min_price']}-{params['max_price']}元")
    elif params.get("min_price"):
        parts.append(f"{params['min_price']}元以上")
    elif params.get("max_price"):
        parts.append(f"{params['max_price']}元以下")

    if intent == "rental":
        type_map = {"whole": "整租", "shared": "合租", "single": "单间"}
        if params.get("type"):
            parts.append(type_map.get(params["type"], ""))
    elif intent == "trade":
        if params.get("category"):
            category_map = {"furniture": "家具", "appliance": "家电"}
            parts.append(category_map.get(params["category"], params["category"]))

    if parts:
        return f"为您找到{''.join(parts)}"
    else:
        return "为您找到相关结果"

def _generate_suggestions(params: Dict[str, Any], intent: str) -> List[str]:
    """Generate suggestions when no results found"""
    suggestions = []

    if params.get("min_price") or params.get("max_price"):
        suggestions.append("尝试调整价格范围")

    if params.get("location"):
        suggestions.append("尝试搜索附近区域")

    if intent == "rental" and params.get("type"):
        suggestions.append("尝试其他租赁类型")

    if not suggestions:
        suggestions.append("尝试使用不同的关键词")

    return suggestions
