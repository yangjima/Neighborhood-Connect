import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app
from tests.conftest import (
    _make_mock_httpx_client,
    _build_workflow,
    mock_parameter_extractor_rental,
    mock_parameter_extractor_trade,
    mock_data_retrieval,
)
import app.main as main_module


@pytest.mark.asyncio
async def test_end_to_end_rental_search(test_workflow):
    """Test complete rental search flow."""
    # Build workflow with rental-specific mock parameter extractor and mock data
    rental_json = {
        "data": [
            {"id": "rental_1", "title": "精装两室", "price": 3000},
            {"id": "rental_2", "title": "温馨两居", "price": 2800}
        ],
        "total": 2
    }

    workflow = _build_workflow(
        parameter_extractor_fn=mock_parameter_extractor_rental,
        data_retrieval_fn=mock_data_retrieval(rental_json),
    )
    main_module.workflow = workflow

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

    # Verify response structure
    assert data["success"] is True
    assert "query_understanding" in data
    assert "望京" in data["query_understanding"]
    assert "applied_filters" in data
    assert data["applied_filters"]["location"] == "望京"
    assert 2700 <= data["applied_filters"]["min_price"] <= 3000
    assert 3000 <= data["applied_filters"]["max_price"] <= 3301  # Allow slight floating point error


@pytest.mark.asyncio
async def test_end_to_end_trade_search(test_workflow):
    """Test complete trade search flow."""
    # Build workflow with trade-specific mock parameter extractor and mock data
    trade_json = {
        "data": [{"id": "item_1", "title": "布艺沙发", "price": 1200}],
        "total": 1
    }

    workflow = _build_workflow(
        parameter_extractor_fn=mock_parameter_extractor_trade,
        data_retrieval_fn=mock_data_retrieval(trade_json),
    )
    main_module.workflow = workflow

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/ai/smart-search",
            json={
                "query": "九成新的沙发",
                "context": "trade"
            }
        )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert "沙发" in data["query_understanding"] or "家具" in data["query_understanding"]


@pytest.mark.asyncio
async def test_low_confidence_query(test_workflow):
    """Test handling of ambiguous queries."""
    # Uses the default workflow from the test_workflow fixture
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/ai/smart-search",
            json={
                "query": "我想要",
                "context": "rental"
            }
        )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is False
    assert "更多信息" in data["error"]
    assert "suggestions" in data


@pytest.mark.asyncio
async def test_metrics_endpoint(test_workflow):
    """Test Prometheus metrics endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as client:
        response = await client.get("/metrics")

    assert response.status_code == 200
    assert "ai_requests_total" in response.text
