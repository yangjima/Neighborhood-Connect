from app.models.schemas import RentalParams, TradeParams
from app.models.state import ConversationState


def test_conversation_state_structure():
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
        metadata={},
    )

    assert state["user_query"] == "望京3000左右的两室一厅"
    assert state["context"] == "rental"
    assert state["intent"] == "rental"
    assert state["intent_confidence"] == 0.95


def test_rental_params_validation():
    params = RentalParams(
        type="whole",
        location="望京",
        min_price=2700.0,
        max_price=3300.0,
        min_area=None,
        max_area=None,
        facilities=None,
    )

    assert params.type == "whole"
    assert params.location == "望京"
    assert params.min_price == 2700.0


def test_trade_params_validation():
    params = TradeParams(
        category="furniture",
        condition="like_new",
        location="朝阳区",
        min_price=1000.0,
        max_price=2000.0,
    )

    assert params.category == "furniture"
    assert params.condition == "like_new"
