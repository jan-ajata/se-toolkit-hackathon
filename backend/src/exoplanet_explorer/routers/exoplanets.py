"""Router for exoplanet endpoints."""

import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from exoplanet_explorer.calculator import calculate_survival_metrics
from exoplanet_explorer.database import get_session
from exoplanet_explorer.db.exoplanets import (
    read_exoplanet,
    read_exoplanet_stats,
    read_exoplanets,
)
from exoplanet_explorer.models.exoplanet import (
    CalculateRequest,
    CalculateResponse,
    CompareRequest,
    CompareResponse,
    ExoplanetListResponse,
    ExoplanetResponse,
    ExoplanetStats,
    PlanetOfDayResponse,
)
from exoplanet_explorer.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)


def _to_response(record) -> ExoplanetResponse:
    """Convert DB record to API response, computing habitable zone flag."""
    insolation = record.insolation_flux
    habitable = insolation is not None and 0.25 <= insolation <= 1.1
    return ExoplanetResponse(
        id=record.id,
        name=record.name,
        hostname=record.hostname,
        discovery_year=record.discovery_year,
        discovery_method=record.discovery_method,
        radius_earth=record.radius_earth,
        mass_earth=record.mass_earth,
        orbital_period_days=record.orbital_period_days,
        equilibrium_temperature_k=record.equilibrium_temperature_k,
        distance_light_years=record.distance_light_years,
        semi_major_axis_au=record.semi_major_axis_au,
        insolation_flux=record.insolation_flux,
        habitable_zone=habitable,
    )


@router.get("/", response_model=ExoplanetListResponse)
async def get_exoplanets(
    search: str | None = Query(None, description="Search by planet name"),
    min_radius: float | None = Query(None, description="Minimum radius (Earth radii)"),
    max_radius: float | None = Query(None, description="Maximum radius (Earth radii)"),
    min_mass: float | None = Query(None, description="Minimum mass (Earth masses)"),
    max_mass: float | None = Query(None, description="Maximum mass (Earth masses)"),
    habitable_zone: bool | None = Query(None, description="Filter by habitable zone"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    session: AsyncSession = Depends(get_session),
):
    """List exoplanets with optional filtering and pagination."""
    try:
        items, total = await read_exoplanets(
            session,
            search=search,
            min_radius=min_radius,
            max_radius=max_radius,
            min_mass=min_mass,
            max_mass=max_mass,
            habitable_zone=habitable_zone,
            page=page,
            page_size=page_size,
        )
    except Exception as exc:
        logger.warning(
            "exoplanets_list_failed",
            extra={"event": "exoplanets_list_failed", "error": str(exc)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve exoplanets",
        ) from exc

    return ExoplanetListResponse(
        items=[_to_response(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/stats", response_model=ExoplanetStats)
async def get_stats(session: AsyncSession = Depends(get_session)):
    """Get aggregate catalog statistics."""
    try:
        stats = await read_exoplanet_stats(session)
        return ExoplanetStats(**stats)
    except Exception as exc:
        logger.warning(
            "stats_failed",
            extra={"event": "stats_failed", "error": str(exc)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compute statistics",
        ) from exc


@router.post("/calculate", response_model=CalculateResponse)
async def calculate_survival(
    body: CalculateRequest,
    session: AsyncSession = Depends(get_session),
):
    """Calculate survival metrics for a given exoplanet.

    Send a planet ID and your Earth weight to see:
    - Your weight on that planet
    - Surface gravity
    - Travel time at various speeds
    - Temperature and gravity verdicts
    """
    planet = await read_exoplanet(session, body.planet_id)
    if planet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exoplanet not found",
        )

    metrics = calculate_survival_metrics(
        planet_name=planet.name,
        user_weight_kg=body.user_weight_kg,
        planet_mass_earth=planet.mass_earth,
        planet_radius_earth=planet.radius_earth,
        distance_light_years=planet.distance_light_years,
        temperature_k=planet.equilibrium_temperature_k,
    )
    return CalculateResponse(**metrics)


@router.post("/compare", response_model=CompareResponse)
async def compare_planets(
    body: CompareRequest,
    session: AsyncSession = Depends(get_session),
):
    """Compare two exoplanets using AI.

    Send two planet IDs to get a natural-language comparison paragraph
    generated by an LLM (if LLM is enabled).
    """
    planet_a = await read_exoplanet(session, body.planet_a_id)
    planet_b = await read_exoplanet(session, body.planet_b_id)

    if planet_a is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exoplanet A (id={body.planet_a_id}) not found",
        )
    if planet_b is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exoplanet B (id={body.planet_b_id}) not found",
        )

    response_a = _to_response(planet_a)
    response_b = _to_response(planet_b)

    if settings.llm_enabled:
        try:
            from exoplanet_explorer.llm import compare_planets as llm_compare

            comparison_text = await llm_compare(response_a, response_b)
        except Exception as e:
            logger.warning(
                "llm_comparison_failed",
                extra={"event": "llm_comparison_failed", "error": str(e)},
            )
            hab_a = "in habitable zone" if response_a.habitable_zone else "outside habitable zone"
            hab_b = "in habitable zone" if response_b.habitable_zone else "outside habitable zone"
            comparison_text = (
                f"AI comparison unavailable. Here are the raw stats:\n\n"
                f"**{response_a.name}**: radius {response_a.radius_earth}× Earth, "
                f"distance {response_a.distance_light_years} ly, "
                f"{hab_a}.\n"
                f"**{response_b.name}**: radius {response_b.radius_earth}× Earth, "
                f"distance {response_b.distance_light_years} ly, "
                f"{hab_b}."
            )
    else:
        hab_a = "in habitable zone" if response_a.habitable_zone else "outside habitable zone"
        hab_b = "in habitable zone" if response_b.habitable_zone else "outside habitable zone"
        comparison_text = (
            f"LLM not configured. Set LLM_API_KEY to enable AI comparisons.\n\n"
            f"**{response_a.name}**: radius {response_a.radius_earth}× Earth, "
            f"distance {response_a.distance_light_years} ly, "
            f"{hab_a}.\n"
            f"**{response_b.name}**: radius {response_b.radius_earth}× Earth, "
            f"distance {response_b.distance_light_years} ly, "
            f"{hab_b}."
        )

    return CompareResponse(
        planet_a=response_a,
        planet_b=response_b,
        comparison=comparison_text,
    )


@router.get("/planet-of-the-day", response_model=PlanetOfDayResponse)
async def planet_of_the_day(
    session: AsyncSession = Depends(get_session),
):
    """Get a featured exoplanet of the day with a fun AI-generated fact.

    Picks a planet based on the current date and generates a fun fact
    using an LLM (if enabled).
    """
    # Get all planets to pick one deterministically based on date
    try:
        items, total = await read_exoplanets(session, page=1, page_size=365)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve exoplanets",
        ) from exc

    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No exoplanets in catalog",
        )

    # Pick a planet based on the day of the year
    today = datetime.date.today()
    day_of_year = today.timetuple().tm_yday
    planet = items[day_of_year % len(items)]
    planet_response_obj = _to_response(planet)

    if settings.llm_enabled:
        try:
            from exoplanet_explorer.llm import generate_fun_fact as llm_fact

            fun_fact = await llm_fact(planet_response_obj)
        except Exception as e:
            logger.warning(
                "llm_fun_fact_failed",
                extra={"event": "llm_fun_fact_failed", "error": str(e)},
            )
            fun_fact = (
                f"{planet_response_obj.name} was discovered in {planet_response_obj.discovery_year} "
                f"using the {planet_response_obj.discovery_method} method. "
                f"It has a radius of {planet_response_obj.radius_earth}× Earth and is "
                f"{planet_response_obj.distance_light_years} light-years away."
            )
    else:
        fun_fact = (
            f"LLM not configured. Set LLM_API_KEY to enable AI fun facts.\n\n"
            f"{planet_response_obj.name} was discovered in {planet_response_obj.discovery_year} "
            f"using the {planet_response_obj.discovery_method} method. "
            f"It has a radius of {planet_response_obj.radius_earth}× Earth and is "
            f"{planet_response_obj.distance_light_years} light-years away."
        )

    return PlanetOfDayResponse(
        planet=planet_response_obj,
        fun_fact=fun_fact,
    )


@router.get("/{planet_id}", response_model=ExoplanetResponse)
async def get_exoplanet(
    planet_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get a single exoplanet by ID."""
    planet = await read_exoplanet(session, planet_id)
    if planet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exoplanet not found",
        )
    return _to_response(planet)
