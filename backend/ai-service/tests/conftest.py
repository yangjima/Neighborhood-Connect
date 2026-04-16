import pytest
from unittest.mock import AsyncMock, MagicMock
from langgraph.graph import END
from app.models.state import ConversationState


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
def _make_mock_httpx_client(json_data: dict):
    """Build a mock httpx AsyncClient that returns the given JSON data."""
    mock_response = MagicMock()
    mock_response.json.return_value = json_data
    mock_response.raise_for_status = MagicMock()
    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    return mock_client


# ---------------------------------------------------------------------------
# Per-test fixture: provides a fresh mock httpx client for each test
# ---------------------------------------------------------------------------
@pytest.fixture
def mock_httpx_client():
    """Override this in individual tests to provide specific API responses."""
    return _make_mock_httpx_client({"data": [], "total": 0})


# ---------------------------------------------------------------------------
# Internal helpers for building test workflows
# ---------------------------------------------------------------------------
def _route_after_intent(state: ConversationState) -> str:
    if state["intent_confidence"] >= 0.7:
        return "continue"
    return "low_confidence"


async def _handle_low_confidence(state: ConversationState) -> ConversationState:
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


def _build_workflow(parameter_extractor_fn, data_retrieval_fn):
    """Build a test workflow with the given agent functions."""
    from langgraph.graph import StateGraph
    from app.agents.intent_classifier import intent_classifier_agent
    from app.agents.query_optimizer import query_optimizer_agent
    from app.agents.response_formatter import response_formatter_agent

    workflow = StateGraph(ConversationState)
    workflow.add_node("intent_classifier", intent_classifier_agent)
    workflow.add_node("parameter_extractor", parameter_extractor_fn)
    workflow.add_node("query_optimizer", query_optimizer_agent)
    workflow.add_node("data_retrieval", data_retrieval_fn)
    workflow.add_node("response_formatter", response_formatter_agent)
    workflow.add_node("handle_low_confidence", _handle_low_confidence)

    workflow.set_entry_point("intent_classifier")
    workflow.add_conditional_edges(
        "intent_classifier",
        _route_after_intent,
        {"continue": "parameter_extractor", "low_confidence": "handle_low_confidence"}
    )
    workflow.add_edge("parameter_extractor", "query_optimizer")
    workflow.add_edge("query_optimizer", "data_retrieval")
    workflow.add_edge("data_retrieval", "response_formatter")
    workflow.add_edge("response_formatter", END)
    workflow.add_edge("handle_low_confidence", END)

    return workflow.compile()


# ---------------------------------------------------------------------------
# Mock agents for tests
# ---------------------------------------------------------------------------
async def mock_parameter_extractor_rental(state: ConversationState) -> ConversationState:
    """Mock parameter extractor for rental queries (keyword-based, no LLM)."""
    from app.agents.parameter_extractor import _extract_rental_params_fallback
    state["extracted_params"] = _extract_rental_params_fallback(state["user_query"])
    return state


async def mock_parameter_extractor_trade(state: ConversationState) -> ConversationState:
    """Mock parameter extractor for trade queries (keyword-based, no LLM)."""
    from app.agents.parameter_extractor import _extract_trade_params_fallback
    state["extracted_params"] = _extract_trade_params_fallback(state["user_query"])
    return state


def mock_data_retrieval(json_data: dict):
    """Factory: create a mock data_retrieval agent that returns the given data.

    Note: this is a regular (non-async) factory that returns an async function.
    Usage: mock_data_retrieval(some_json)(state) -> awaitable
    """
    async def agent(state: ConversationState) -> ConversationState:
        state["retrieved_data"] = json_data.get("data", [])
        state["metadata"]["cache_hit"] = False
        return state
    return agent


# ---------------------------------------------------------------------------
# Function-scoped fixture: ensures app.main.workflow is never None
# ---------------------------------------------------------------------------
@pytest.fixture(scope="function")
def test_workflow():
    """Function-scoped fixture that initializes app.main.workflow before each test.

    This prevents test order/state interference where app.main.workflow could
    become None between tests (e.g., due to event loop scoping issues with
    session-scoped fixtures in pytest-asyncio).

    Tests that need custom agents should replace app.main.workflow directly
    within the test body. This fixture guarantees the baseline workflow exists.
    """
    import app.main as main_module

    # Use the same fallback-based workflow as the default for baseline tests
    from app.agents.parameter_extractor import (
        _extract_rental_params_fallback,
        _extract_trade_params_fallback,
    )

    async def default_param_extractor(state: ConversationState) -> ConversationState:
        if state["intent"] == "rental":
            state["extracted_params"] = _extract_rental_params_fallback(state["user_query"])
        else:
            state["extracted_params"] = _extract_trade_params_fallback(state["user_query"])
        return state

    async def default_data_retrieval(state: ConversationState) -> ConversationState:
        state["retrieved_data"] = []
        state["metadata"]["cache_hit"] = False
        return state

    main_module.workflow = _build_workflow(default_param_extractor, default_data_retrieval)

    yield main_module.workflow

    # Cleanup
    main_module.workflow = None
