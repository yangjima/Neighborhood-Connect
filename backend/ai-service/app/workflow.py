from langgraph.graph import StateGraph, END
from app.models.state import ConversationState
from app.agents.intent_classifier import intent_classifier_agent
from app.agents.parameter_extractor import parameter_extractor_agent
from app.agents.query_optimizer import query_optimizer_agent
from app.agents.data_retrieval import data_retrieval_agent
from app.agents.response_formatter import response_formatter_agent

def create_workflow() -> StateGraph:
    """
    Create the LangGraph workflow for AI smart search.

    Workflow:
    1. IntentClassifier - identify rental vs trade
    2. Conditional routing based on confidence
    3. ParameterExtractor - extract structured params
    4. QueryOptimizer - expand synonyms and locations
    5. DataRetrieval - call backend APIs
    6. ResponseFormatter - format for frontend
    """
    workflow = StateGraph(ConversationState)

    # Add nodes
    workflow.add_node("intent_classifier", intent_classifier_agent)
    workflow.add_node("parameter_extractor", parameter_extractor_agent)
    workflow.add_node("query_optimizer", query_optimizer_agent)
    workflow.add_node("data_retrieval", data_retrieval_agent)
    workflow.add_node("response_formatter", response_formatter_agent)
    workflow.add_node("handle_low_confidence", handle_low_confidence)

    # Set entry point
    workflow.set_entry_point("intent_classifier")

    # Add conditional edges
    workflow.add_conditional_edges(
        "intent_classifier",
        route_after_intent,
        {
            "continue": "parameter_extractor",
            "low_confidence": "handle_low_confidence"
        }
    )

    # Add sequential edges
    workflow.add_edge("parameter_extractor", "query_optimizer")
    workflow.add_edge("query_optimizer", "data_retrieval")
    workflow.add_edge("data_retrieval", "response_formatter")
    workflow.add_edge("response_formatter", END)
    workflow.add_edge("handle_low_confidence", END)

    return workflow.compile()

def route_after_intent(state: ConversationState) -> str:
    """Route based on intent confidence"""
    if state["intent_confidence"] >= 0.7:
        return "continue"
    else:
        return "low_confidence"

async def handle_low_confidence(state: ConversationState) -> ConversationState:
    """Handle queries with low confidence"""
    state["formatted_response"] = {
        "success": False,
        "error": "需要更多信息来理解您的查询,请提供更具体的描述",
        "data": [],
        "total": 0,
        "suggestions": [
            "请说明您是想租房还是购买二手商品",
            "提供更多细节,如位置、价格范围等"
        ]
    }
    return state
