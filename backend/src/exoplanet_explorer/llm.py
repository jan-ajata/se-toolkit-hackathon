"""LLM client for AI-powered exoplanet comparisons and fun facts.

Uses httpx to call any OpenAI-compatible API endpoint.
"""

import logging

import httpx

from exoplanet_explorer.models.exoplanet import ExoplanetResponse
from exoplanet_explorer.settings import settings

logger = logging.getLogger(__name__)

COMPARISON_PROMPT = """\
You are an enthusiastic science communicator writing for a general audience.
Compare these two confirmed exoplanets in an engaging, accessible way.
Mention their size, temperature, distance from Earth, and whether they could
potentially support life. Keep it under 150 words. Be specific with numbers.

Planet A: {name_a} — radius {radius_a}× Earth, mass {mass_a}× Earth, \
temperature {temp_a}K, distance {dist_a} ly, \
{hab_a}, \
discovered {year_a}.

Planet B: {name_b} — radius {radius_b}× Earth, mass {mass_b}× Earth, \
temperature {temp_b}K, distance {dist_b} ly, \
{hab_b}, \
discovered {year_b}.
"""

FUN_FACT_PROMPT = """\
You are an enthusiastic science communicator writing for a general audience.
Generate a fun, accessible fact about this exoplanet in 2-3 sentences.
Make it engaging for students and space enthusiasts. Mention interesting
numbers and comparisons to Earth. Be specific.

Planet: {name} — radius {radius}× Earth, mass {mass}× Earth, \
temperature {temp}K, distance {dist} ly, \
{hab}, \
discovered {year}, detected by {method}.
"""


def _format_planet(planet: ExoplanetResponse) -> dict:
    """Helper to format planet data for prompts."""
    hab_text = "in the habitable zone" if planet.habitable_zone else "outside the habitable zone"
    return {
        "name": planet.name,
        "radius": planet.radius_earth,
        "mass": planet.mass_earth if planet.mass_earth is not None else "unknown",
        "temp": planet.equilibrium_temperature_k
        if planet.equilibrium_temperature_k is not None
        else "unknown",
        "dist": planet.distance_light_years
        if planet.distance_light_years is not None
        else "unknown",
        "hab": hab_text,
        "year": planet.discovery_year,
        "method": planet.discovery_method,
    }


async def compare_planets(
    planet_a: ExoplanetResponse,
    planet_b: ExoplanetResponse,
) -> str:
    """Generate a natural-language comparison of two exoplanets."""
    a = _format_planet(planet_a)
    b = _format_planet(planet_b)

    prompt = COMPARISON_PROMPT.format(
        name_a=a["name"],
        radius_a=a["radius"],
        mass_a=a["mass"],
        temp_a=a["temp"],
        dist_a=a["dist"],
        hab_a=a["hab"],
        year_a=a["year"],
        name_b=b["name"],
        radius_b=b["radius"],
        mass_b=b["mass"],
        temp_b=b["temp"],
        dist_b=b["dist"],
        hab_b=b["hab"],
        year_b=b["year"],
    )

    return await _call_llm(prompt)


async def generate_fun_fact(planet: ExoplanetResponse) -> str:
    """Generate a fun, accessible fact about an exoplanet."""
    p = _format_planet(planet)

    prompt = FUN_FACT_PROMPT.format(
        name=p["name"],
        radius=p["radius"],
        mass=p["mass"],
        temp=p["temp"],
        dist=p["dist"],
        hab=p["hab"],
        year=p["year"],
        method=p["method"],
    )

    return await _call_llm(prompt)


async def _call_llm(prompt: str) -> str:
    """Make the actual LLM API call."""
    if not settings.llm_enabled:
        raise RuntimeError("LLM is not enabled. Set LLM_API_KEY to use this feature.")

    url = f"{settings.llm_api_base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.llm_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 300,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except httpx.HTTPStatusError as e:
            logger.error(
                "llm_http_error",
                extra={
                    "event": "llm_http_error",
                    "status": e.response.status_code,
                    "body": e.response.text[:500],
                },
            )
            raise RuntimeError(f"LLM API error: {e.response.status_code}") from e
        except (KeyError, IndexError) as e:
            logger.error(
                "llm_parse_error",
                extra={"event": "llm_parse_error", "error": str(e)},
            )
            raise RuntimeError("Failed to parse LLM response") from e
