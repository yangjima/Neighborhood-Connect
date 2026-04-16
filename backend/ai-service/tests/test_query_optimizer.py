import pytest
from app.agents.query_optimizer import query_optimizer_agent
from app.models.state import ConversationState

@pytest.mark.asyncio
async def test_optimize_location_expansion():
    state = ConversationState(
        user_query="望京的房子",
        context="rental",
        intent="rental",
        intent_confidence=0.95,
        extracted_params={"location": "望京"},
        optimized_query={},
        retrieved_data=[],
        formatted_response={},
        error=None,
        metadata={}
    )

    result = await query_optimizer_agent(state)
    optimized = result["optimized_query"]

    assert "location" in optimized
    assert isinstance(optimized["location"], list)
    assert "望京" in optimized["location"]
    assert len(optimized["location"]) > 1

@pytest.mark.asyncio
async def test_optimize_price_range():
    state = ConversationState(
        user_query="3000左右",
        context="rental",
        intent="rental",
        intent_confidence=0.95,
        extracted_params={"min_price": 2700, "max_price": 3300},
        optimized_query={},
        retrieved_data=[],
        formatted_response={},
        error=None,
        metadata={}
    )

    result = await query_optimizer_agent(state)
    optimized = result["optimized_query"]

    assert optimized["min_price"] == 2700
    assert optimized["max_price"] == 3300

@pytest.mark.asyncio
async def test_optimize_category_synonyms():
    state = ConversationState(
        user_query="沙发",
        context="trade",
        intent="trade",
        intent_confidence=0.92,
        extracted_params={"category": "furniture"},
        optimized_query={},
        retrieved_data=[],
        formatted_response={},
        error=None,
        metadata={}
    )

    result = await query_optimizer_agent(state)
    optimized = result["optimized_query"]

    assert "keywords" in optimized
    assert "沙发" in optimized["keywords"]
