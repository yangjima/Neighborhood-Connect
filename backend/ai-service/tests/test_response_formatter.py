import pytest
from app.models.state import ConversationState
from app.agents.response_formatter import response_formatter_agent

@pytest.mark.asyncio
async def test_response_formatter_with_results():
    """Test formatting response with retrieved data"""
    state: ConversationState = {
        "user_query": "望京3000左右的两室一厅",
        "context": "rental",
        "intent": "rental",
        "intent_confidence": 0.95,
        "extracted_params": {
            "location": "望京",
            "min_price": 2700,
            "max_price": 3300,
            "type": "whole"
        },
        "optimized_query": {
            "location": ["望京", "朝阳区望京"],
            "min_price": 2700,
            "max_price": 3300,
            "type": "whole"
        },
        "retrieved_data": [
            {"id": "rental_1", "title": "精装两室", "price": 3000},
            {"id": "rental_2", "title": "温馨两居", "price": 2800}
        ],
        "formatted_response": {},
        "error": None,
        "metadata": {}
    }

    result = await response_formatter_agent(state)

    assert result["formatted_response"]["success"] is True
    assert result["formatted_response"]["total"] == 2
    assert len(result["formatted_response"]["data"]) == 2
    assert "query_understanding" in result["formatted_response"]
    assert "望京" in result["formatted_response"]["query_understanding"]
    assert "applied_filters" in result["formatted_response"]

@pytest.mark.asyncio
async def test_response_formatter_no_results():
    """Test formatting response with no results"""
    state: ConversationState = {
        "user_query": "火星上的房子",
        "context": "rental",
        "intent": "rental",
        "intent_confidence": 0.95,
        "extracted_params": {"location": "火星"},
        "optimized_query": {"location": ["火星"]},
        "retrieved_data": [],
        "formatted_response": {},
        "error": None,
        "metadata": {}
    }

    result = await response_formatter_agent(state)

    assert result["formatted_response"]["success"] is True
    assert result["formatted_response"]["total"] == 0
    assert len(result["formatted_response"]["data"]) == 0
    assert "suggestions" in result["formatted_response"]

@pytest.mark.asyncio
async def test_response_formatter_with_error():
    """Test formatting response when error occurred"""
    state: ConversationState = {
        "user_query": "望京的房子",
        "context": "rental",
        "intent": "rental",
        "intent_confidence": 0.95,
        "extracted_params": {},
        "optimized_query": {},
        "retrieved_data": [],
        "formatted_response": {},
        "error": "API timeout",
        "metadata": {}
    }

    result = await response_formatter_agent(state)

    assert result["formatted_response"]["success"] is False
    assert "error" in result["formatted_response"]
    assert result["formatted_response"]["error"] == "API timeout"
