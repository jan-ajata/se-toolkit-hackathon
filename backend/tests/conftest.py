"""Configure test environment before any module imports.

This file MUST be named conftest.py so pytest loads it before collecting tests.
Environment variables must be set BEFORE any module that uses pydantic-settings is imported.
"""

import os
import sys

# Force-set required environment variables for tests (override any existing values)
# NOTE: LLM vars are NOT overridden — if set in the environment, they'll be used
# for live integration tests. Defaults are only set when not provided.
_test_env = {
    "NAME": "Exoplanet Explorer Test",
    "DEBUG": "true",
    "ADDRESS": "0.0.0.0",
    "PORT": "8000",
    "RELOAD": "false",
    "API_KEY": "test-api-key",
    "CORS_ORIGINS": '["http://localhost:3000"]',
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "DB_NAME": "exoplanets_test",
    "DB_USER": "test_user",
    "DB_PASSWORD": "test_pass",
}

for key, value in _test_env.items():
    os.environ[key] = value

# LLM vars — only set defaults if not already in environment
os.environ.setdefault("LLM_API_KEY", "")
os.environ.setdefault("LLM_API_BASE_URL", "https://api.openai.com/v1")
os.environ.setdefault("LLM_MODEL", "gpt-4o-mini")

# Clear any already-imported modules from cache so they'll be re-imported with new env
_modules_to_clear = [m for m in sys.modules if m.startswith("exoplanet_explorer")]
for mod in _modules_to_clear:
    del sys.modules[mod]


import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Create a fresh SQLite in-memory database for each test using SQLModel AsyncSession."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # Use SQLModel's AsyncSession which has .exec() method
    async_session = AsyncSession(bind=engine)
    yield async_session
    await async_session.close()
    await engine.dispose()
