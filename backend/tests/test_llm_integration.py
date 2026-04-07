"""Integration test for the LLM module — requires a running LLM server.

Run only on the university VM where the LLM server is accessible:
    cd backend && uv run pytest tests/test_llm_integration.py -v --llm-live

Skip by default — requires LLM_API_KEY to be set and server reachable.
"""

import pytest

from exoplanet_explorer.models.exoplanet import ExoplanetResponse
from exoplanet_explorer.settings import settings


def _make_planet(**overrides) -> ExoplanetResponse:
    """Helper to create a test ExoplanetResponse."""
    defaults = {
        "id": 1,
        "name": "Kepler-442b",
        "hostname": "Kepler-442",
        "discovery_year": 2015,
        "discovery_method": "Transit",
        "radius_earth": 1.34,
        "mass_earth": 2.3,
        "orbital_period_days": 112.3,
        "equilibrium_temperature_k": 260.0,
        "distance_light_years": 1206.0,
        "semi_major_axis_au": 0.409,
        "insolation_flux": 0.57,
        "habitable_zone": True,
    }
    defaults.update(overrides)
    return ExoplanetResponse(**defaults)


@pytest.mark.asyncio
@pytest.mark.llm_live
@pytest.mark.skipif(not settings.llm_enabled, reason="LLM not configured (set LLM_API_KEY)")
async def test_compare_planets_live():
    """Test actual LLM comparison with real server."""
    planet_a = _make_planet(id=1, name="Kepler-442b", radius_earth=1.34, distance_light_years=1206)
    planet_b = _make_planet(id=2, name="Proxima Centauri b", radius_earth=1.03, distance_light_years=4.24)

    from exoplanet_explorer.llm import compare_planets

    result = await compare_planets(planet_a, planet_b)

    assert isinstance(result, str)
    assert len(result) > 20  # Should be a meaningful paragraph
    # Should mention at least one planet name
    assert "Kepler-442b" in result or "Proxima Centauri b" in result or "planet" in result.lower()


@pytest.mark.asyncio
@pytest.mark.llm_live
@pytest.mark.skipif(not settings.llm_enabled, reason="LLM not configured (set LLM_API_KEY)")
async def test_generate_fun_fact_live():
    """Test actual LLM fun fact generation with real server."""
    planet = _make_planet(name="TRAPPIST-1e", radius_earth=0.92, discovery_year=2017)

    from exoplanet_explorer.llm import generate_fun_fact

    result = await generate_fun_fact(planet)

    assert isinstance(result, str)
    assert len(result) > 20  # Should be a meaningful fact
    # Should mention the planet name
    assert "TRAPPIST-1e" in result or "planet" in result.lower()


@pytest.mark.asyncio
@pytest.mark.llm_live
@pytest.mark.skipif(not settings.llm_enabled, reason="LLM not configured (set LLM_API_KEY)")
async def test_llm_settings_valid():
    """Verify that LLM settings are loaded correctly."""
    assert settings.llm_enabled, "LLM_API_KEY should be set for live tests"
    assert settings.llm_api_base_url, "LLM_API_BASE_URL should be set"
    assert settings.llm_model, "LLM_MODEL should be set"
    # Should be using the university VM's local LLM server
    assert settings.llm_model == "coder-model"
