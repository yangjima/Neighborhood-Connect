# backend/ai-service/tests/test_parameter_extractor.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.agents.parameter_extractor import parameter_extractor_agent
from app.models.state import ConversationState

@pytest.mark.asyncio
async def test_extract_rental_parameters():
    state = ConversationState(
        user_query="望京3000左右的两室一厅",
        context="rental",
        intent="rental",
        intent_confidence=0.95,
        extracted_params={},
        optimized_query={},
        retrieved_data=[],
        formatted_response={},
        error=None,
        metadata={}
    )

    # Mock the entire chain
    mock_response = MagicMock()
    mock_response.additional_kwargs = {
        "function_call": {
            "name": "extract_rental_params",
            "arguments": '{"location": "望京", "min_price": 2700, "max_price": 3300}'
        }
    }

    with patch("app.agents.parameter_extractor.ChatPromptTemplate.from_messages") as mock_prompt:
        mock_chain = AsyncMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)

        mock_prompt_instance = MagicMock()
        mock_prompt_instance.__or__ = MagicMock(return_value=mock_chain)
        mock_prompt.return_value = mock_prompt_instance

        result = await parameter_extractor_agent(state)
        params = result["extracted_params"]

        assert params["location"] == "望京"
        assert 2700 <= params["min_price"] <= 3000
        assert 3000 <= params["max_price"] <= 3300

@pytest.mark.asyncio
async def test_extract_trade_parameters():
    state = ConversationState(
        user_query="1000到2000的二手沙发",
        context="trade",
        intent="trade",
        intent_confidence=0.92,
        extracted_params={},
        optimized_query={},
        retrieved_data=[],
        formatted_response={},
        error=None,
        metadata={}
    )

    # Mock the entire chain
    mock_response = MagicMock()
    mock_response.additional_kwargs = {
        "function_call": {
            "name": "extract_trade_params",
            "arguments": '{"category": "furniture", "min_price": 1000, "max_price": 2000}'
        }
    }

    with patch("app.agents.parameter_extractor.ChatPromptTemplate.from_messages") as mock_prompt:
        mock_chain = AsyncMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)

        mock_prompt_instance = MagicMock()
        mock_prompt_instance.__or__ = MagicMock(return_value=mock_chain)
        mock_prompt.return_value = mock_prompt_instance

        result = await parameter_extractor_agent(state)
        params = result["extracted_params"]

        assert params["category"] == "furniture"
        assert params["min_price"] == 1000
        assert params["max_price"] == 2000

@pytest.mark.asyncio
async def test_extract_partial_parameters():
    state = ConversationState(
        user_query="朝阳区的房子",
        context="rental",
        intent="rental",
        intent_confidence=0.88,
        extracted_params={},
        optimized_query={},
        retrieved_data=[],
        formatted_response={},
        error=None,
        metadata={}
    )

    # Mock the entire chain
    mock_response = MagicMock()
    mock_response.additional_kwargs = {
        "function_call": {
            "name": "extract_rental_params",
            "arguments": '{"location": "朝阳区"}'
        }
    }

    with patch("app.agents.parameter_extractor.ChatPromptTemplate.from_messages") as mock_prompt:
        mock_chain = AsyncMock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)

        mock_prompt_instance = MagicMock()
        mock_prompt_instance.__or__ = MagicMock(return_value=mock_chain)
        mock_prompt.return_value = mock_prompt_instance

        result = await parameter_extractor_agent(state)
        params = result["extracted_params"]

        assert params["location"] == "朝阳区"
        assert "min_price" not in params or params["min_price"] is None
