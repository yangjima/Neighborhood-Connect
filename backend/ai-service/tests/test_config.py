import pytest
from pydantic import ValidationError
from app.config import Settings

def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test123")
    monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379")

    settings = Settings()

    assert settings.OPENAI_API_KEY == "sk-test123"
    assert settings.MONGODB_URL == "mongodb://localhost:27017"
    assert settings.REDIS_URL == "redis://localhost:6379"
    assert settings.OPENAI_MODEL == "gpt-4-turbo"  # default
    assert settings.OPENAI_TEMPERATURE == 0.0  # default

def test_settings_validates_required_fields(monkeypatch, tmp_path):
    # Clear the required field and change to a temp directory without .env
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValidationError):
        Settings()
