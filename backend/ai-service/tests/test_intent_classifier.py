import pytest

from app.agents.intent_classifier import intent_classifier_agent
from app.models.state import ConversationState


@pytest.mark.asyncio
async def test_classify_rental_intent():
    state = ConversationState(
        user_query="我想租房",
        context="rental",
        intent="",
        intent_confidence=0.0,
        extracted_params={},
        optimized_query={},
        retrieved_data=[],
        formatted_response={},
        error=None,
        metadata={},
    )

    result = await intent_classifier_agent(state)

    assert result["intent"] == "rental"
    assert result["intent_confidence"] >= 0.7


@pytest.mark.asyncio
async def test_classify_trade_intent():
    state = ConversationState(
        user_query="我想买二手沙发",
        context="trade",
        intent="",
        intent_confidence=0.0,
        extracted_params={},
        optimized_query={},
        retrieved_data=[],
        formatted_response={},
        error=None,
        metadata={},
    )

    result = await intent_classifier_agent(state)

    assert result["intent"] == "trade"
    assert result["intent_confidence"] >= 0.7


@pytest.mark.asyncio
async def test_low_confidence_intent():
    state = ConversationState(
        user_query="你好",
        context="rental",
        intent="",
        intent_confidence=0.0,
        extracted_params={},
        optimized_query={},
        retrieved_data=[],
        formatted_response={},
        error=None,
        metadata={},
    )

    result = await intent_classifier_agent(state)

    assert result["intent_confidence"] < 0.7
