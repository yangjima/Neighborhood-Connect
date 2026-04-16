import pytest
from app.database import get_database, close_database_connection

@pytest.mark.asyncio
async def test_get_database_returns_motor_database():
    db = await get_database()
    assert db is not None
    assert db.name == "neighborhood_db"

@pytest.mark.asyncio
async def test_database_connection_can_ping():
    db = await get_database()
    result = await db.command("ping")
    assert result["ok"] == 1.0
    await close_database_connection()
