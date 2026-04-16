from typing import Any, Dict, List, Optional, TypedDict


class ConversationState(TypedDict):
    # Input
    user_query: str
    context: str

    # Intermediate state
    intent: str
    intent_confidence: float
    extracted_params: Dict[str, Any]
    optimized_query: Dict[str, Any]
    retrieved_data: List[Dict[str, Any]]

    # Output
    formatted_response: Dict[str, Any]

    # Metadata
    error: Optional[str]
    metadata: Dict[str, Any]
