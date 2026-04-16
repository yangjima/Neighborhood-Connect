# backend/ai-service/tests/test_data_retrieval.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.models.state import ConversationState

@pytest.mark.asyncio
async def test_retrieve_rental_data():
    state = ConversationState(
        user_query="望京3000左右的两室一厅",
        context="rental",
        intent="rental",
        intent_confidence=0.95,
        extracted_params={"location": "望京", "min_price": 2700, "max_price": 3300},
        optimized_query={"location": ["望京", "朝阳区望京"], "min_price": 2700, "max_price": 3300},
        retrieved_data=[],
        formatted_response={},
        error=None,
        metadata={}
    )

    mock_response = {
        "data": [{"id": "rental_1", "title": "精装两室", "price": 3000}],
        "total": 1
    }

    # Mock the response object
    mock_resp = MagicMock()
    mock_resp.json.return_value = mock_response
    mock_resp.status_code = 200
    mock_resp.raise_for_status = MagicMock()

    # Mock the AsyncClient context manager
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.agents.data_retrieval.get_cache", new_callable=AsyncMock, return_value=None):
        with patch("app.agents.data_retrieval.set_cache", new_callable=AsyncMock):
            with patch("app.agents.data_retrieval.httpx.AsyncClient", return_value=mock_client):
                from app.agents.data_retrieval import data_retrieval_agent
                result = await data_retrieval_agent(state)

                assert len(result["retrieved_data"]) == 1
                assert result["retrieved_data"][0]["id"] == "rental_1"

@pytest.mark.asyncio
async def test_retrieve_trade_data():
    state = ConversationState(
        user_query="二手沙发",
        context="trade",
        intent="trade",
        intent_confidence=0.92,
        extracted_params={"category": "furniture"},
        optimized_query={"category": "furniture"},
        retrieved_data=[],
        formatted_response={},
        error=None,
        metadata={}
    )

    mock_response = {
        "data": [{"id": "item_1", "title": "布艺沙发", "price": 1200}],
        "total": 1
    }

    # Mock the response object
    mock_resp = MagicMock()
    mock_resp.json.return_value = mock_response
    mock_resp.status_code = 200
    mock_resp.raise_for_status = MagicMock()

    # Mock the AsyncClient context manager
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.agents.data_retrieval.get_cache", new_callable=AsyncMock, return_value=None):
        with patch("app.agents.data_retrieval.set_cache", new_callable=AsyncMock):
            with patch("app.agents.data_retrieval.httpx.AsyncClient", return_value=mock_client):
                from app.agents.data_retrieval import data_retrieval_agent
                result = await data_retrieval_agent(state)

                assert len(result["retrieved_data"]) == 1
                assert result["retrieved_data"][0]["id"] == "item_1"

@pytest.mark.asyncio
async def test_retrieve_with_cache():
    state = ConversationState(
        user_query="望京的房子",
        context="rental",
        intent="rental",
        intent_confidence=0.95,
        extracted_params={"location": "望京"},
        optimized_query={"location": ["望京"]},
        retrieved_data=[],
        formatted_response={},
        error=None,
        metadata={}
    )

    cached_data = [{"id": "rental_1", "title": "缓存房源"}]

    with patch("app.agents.data_retrieval.get_cache", new_callable=AsyncMock) as mock_cache:
        mock_cache.return_value = cached_data

        from app.agents.data_retrieval import data_retrieval_agent
        result = await data_retrieval_agent(state)

        assert result["retrieved_data"] == cached_data
        assert result["metadata"]["cache_hit"] == True
