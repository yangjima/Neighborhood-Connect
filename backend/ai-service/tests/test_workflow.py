import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.workflow import create_workflow
from app.models.state import ConversationState


@pytest.mark.asyncio
async def test_workflow_rental_query():
    """Test complete workflow with rental query"""

    async def mock_data_retrieval(state: ConversationState) -> ConversationState:
        state["retrieved_data"] = [
            {"id": "rental_1", "title": "精装两室", "price": 3000},
            {"id": "rental_2", "title": "温馨两居", "price": 2800}
        ]
        state["metadata"]["cache_hit"] = False
        return state

    with patch("app.workflow.data_retrieval_agent", mock_data_retrieval):
        workflow = create_workflow()

    initial_state: ConversationState = {
        "user_query": "望京3000左右的两室一厅",
        "context": "rental",
        "intent": "",
        "intent_confidence": 0.0,
        "extracted_params": {},
        "optimized_query": {},
        "retrieved_data": [],
        "formatted_response": {},
        "error": None,
        "metadata": {}
    }

    result = await workflow.ainvoke(initial_state)

    assert result["intent"] == "rental"
    assert result["intent_confidence"] >= 0.7
    assert "location" in result["extracted_params"]
    assert result["formatted_response"]["success"] is True

@pytest.mark.asyncio
async def test_workflow_low_confidence():
    """Test workflow with low confidence query"""
    workflow = create_workflow()

    initial_state: ConversationState = {
        "user_query": "我想要",
        "context": "rental",
        "intent": "",
        "intent_confidence": 0.0,
        "extracted_params": {},
        "optimized_query": {},
        "retrieved_data": [],
        "formatted_response": {},
        "error": None,
        "metadata": {}
    }

    result = await workflow.ainvoke(initial_state)

    assert result["intent_confidence"] < 0.7
    assert result["formatted_response"]["success"] is False
    assert "更多信息" in result["formatted_response"].get("error", "")

@pytest.mark.asyncio
async def test_smart_search_endpoint():
    """Test /api/ai/smart-search endpoint"""
    from httpx import AsyncClient, ASGITransport
    from app.main import app
    import app.main as main_module

    async def mock_data_retrieval(state: ConversationState) -> ConversationState:
        state["retrieved_data"] = [
            {"id": "rental_1", "title": "精装两室", "price": 3000}
        ]
        state["metadata"]["cache_hit"] = False
        return state

    with patch("app.workflow.data_retrieval_agent", mock_data_retrieval):
        main_module.workflow = create_workflow()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/ai/smart-search",
            json={
                "query": "望京3000左右的两室一厅",
                "context": "rental"
            }
        )

    assert response.status_code == 200
    data = response.json()

    # Verify response structure (may be success or low confidence)
    assert "success" in data
    assert "data" in data
    assert "total" in data

    # If successful, verify additional fields
    if data["success"]:
        assert "query_understanding" in data
        assert "applied_filters" in data
    else:
        # Low confidence response should have error and suggestions
        assert "error" in data
        assert "suggestions" in data
