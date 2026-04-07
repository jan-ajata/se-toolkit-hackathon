"""Tests for the LLM module — all calls are mocked."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from exoplanet_explorer.models.exoplanet import ExoplanetResponse
from exoplanet_explorer.settings import settings


def _make_planet(**overrides) -> ExoplanetResponse:
    """Helper to create a test ExoplanetResponse."""
    defaults = {
        "id": 1,
        "name": "Test Planet A",
        "hostname": "Test Star",
        "discovery_year": 2020,
        "discovery_method": "Transit",
        "radius_earth": 1.5,
        "mass_earth": 2.0,
        "orbital_period_days": 365.0,
        "equilibrium_temperature_k": 280.0,
        "distance_light_years": 100.0,
        "semi_major_axis_au": 1.0,
        "insolation_flux": 0.8,
        "habitable_zone": True,
    }
    defaults.update(overrides)
    return ExoplanetResponse(**defaults)


@pytest.mark.asyncio
async def test_compare_planets_llm_enabled():
    """Test that compare_planets calls the LLM API with correct prompt."""
    planet_a = _make_planet(id=1, name="Kepler-442b", radius_earth=1.34, distance_light_years=1206)
    planet_b = _make_planet(id=2, name="Proxima Centauri b", radius_earth=1.03, distance_light_years=4.24)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "These two planets are both exciting!"}}]
    }
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("exoplanet_explorer.llm.httpx.AsyncClient", return_value=mock_client):
        with patch.object(settings, "llm_api_key", "test-key"):
            from exoplanet_explorer.llm import compare_planets

            result = await compare_planets(planet_a, planet_b)

            assert result == "These two planets are both exciting!"
            mock_client.post.assert_called_once()

            # Verify the call includes the correct URL (first positional arg)
            call_args = mock_client.post.call_args
            url = call_args[0][0] if call_args[0] else call_args[1].get("url", "")
            assert "chat/completions" in url


@pytest.mark.asyncio
async def test_generate_fun_fact_llm_enabled():
    """Test that generate_fun_fact calls the LLM API."""
    planet = _make_planet(name="TRAPPIST-1e", radius_earth=0.92, discovery_year=2017)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "TRAPPIST-1e is an amazing world!"}}]
    }
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("exoplanet_explorer.llm.httpx.AsyncClient", return_value=mock_client):
        with patch.object(settings, "llm_api_key", "test-key"):
            from exoplanet_explorer.llm import generate_fun_fact

            result = await generate_fun_fact(planet)

            assert result == "TRAPPIST-1e is an amazing world!"


@pytest.mark.asyncio
async def test_compare_planets_llm_disabled():
    """Test that compare_planets raises error when LLM is not enabled."""
    planet_a = _make_planet()
    planet_b = _make_planet()

    with patch.object(settings, "llm_api_key", None):
        from exoplanet_explorer.llm import _call_llm

        with pytest.raises(RuntimeError, match="LLM is not enabled"):
            await _call_llm("test prompt")


@pytest.mark.asyncio
async def test_llm_http_error():
    """Test that HTTP errors are handled gracefully."""
    import httpx

    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"

    mock_client = AsyncMock()
    mock_client.post.side_effect = httpx.HTTPStatusError(
        "Unauthorized", request=MagicMock(), response=mock_response
    )
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("exoplanet_explorer.llm.httpx.AsyncClient", return_value=mock_client):
        with patch.object(settings, "llm_api_key", "bad-key"):
            from exoplanet_explorer.llm import _call_llm

            with pytest.raises(RuntimeError, match="LLM API error: 401"):
                await _call_llm("test prompt")


@pytest.mark.asyncio
async def test_llm_parse_error():
    """Test that malformed responses are handled."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"invalid": "structure"}

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("exoplanet_explorer.llm.httpx.AsyncClient", return_value=mock_client):
        with patch.object(settings, "llm_api_key", "test-key"):
            from exoplanet_explorer.llm import _call_llm

            with pytest.raises(RuntimeError, match="Failed to parse LLM response"):
                await _call_llm("test prompt")
