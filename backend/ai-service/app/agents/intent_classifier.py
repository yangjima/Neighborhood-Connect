from app.models.state import ConversationState
from app.utils.logger import get_logger
import time

logger = get_logger(__name__)

RENTAL_KEYWORDS = {
    "租房",
    "出租",
    "整租",
    "合租",
    "单间",
    "房源",
    "看房",
    "公寓",
    "室",
    "厅",
}

TRADE_KEYWORDS = {
    "买",
    "卖",
    "二手",
    "转让",
    "家具",
    "电器",
    "沙发",
    "冰箱",
    "电视",
}


def _score_intent(query: str, keywords: set[str]) -> float:
    if not query:
        return 0.0
    hit_count = sum(1 for keyword in keywords if keyword in query)
    if hit_count == 0:
        return 0.0
    # 1 hit = 0.75, then saturate near 1.0
    return min(1.0, 0.55 + 0.2 * hit_count)


async def intent_classifier_agent(state: ConversationState) -> ConversationState:
    """Classify user intent into rental or trade with confidence score."""
    start_time = time.time()
    query = state.get("user_query", "")

    try:
        rental_score = _score_intent(query, RENTAL_KEYWORDS)
        trade_score = _score_intent(query, TRADE_KEYWORDS)

        if rental_score == 0 and trade_score == 0:
            state["intent"] = state.get("context", "rental")
            state["intent_confidence"] = 0.3

            duration_ms = (time.time() - start_time) * 1000
            logger.info(
                "intent_classified",
                user_query=query,
                intent=state["intent"],
                confidence=state["intent_confidence"],
                duration_ms=duration_ms
            )
            return state

        if rental_score >= trade_score:
            state["intent"] = "rental"
            state["intent_confidence"] = rental_score
        else:
            state["intent"] = "trade"
            state["intent_confidence"] = trade_score

        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            "intent_classified",
            user_query=query,
            intent=state["intent"],
            confidence=state["intent_confidence"],
            duration_ms=duration_ms
        )

        return state

    except Exception as e:
        logger.error(
            "intent_classification_failed",
            user_query=query,
            error=str(e)
        )
        raise
