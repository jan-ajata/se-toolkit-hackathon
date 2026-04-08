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
        mass_estimated=getattr(record, "mass_estimated", False),
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
    """Compare two exoplanets numerically with side-by-side stats.

    Send two planet IDs to get a detailed numerical comparison
    with Earth reference values.
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

    earth_reference = {
        "radius_earth": 1.0,
        "mass_earth": 1.0,
        "temperature_k": 288,
        "orbital_period_days": 365.25,
        "distance_light_years": 0,
    }

    return CompareResponse(
        planet_a=response_a,
        planet_b=response_b,
        earth_reference=earth_reference,
    )


@router.get("/planet-of-the-day", response_model=PlanetOfDayResponse)
async def planet_of_the_day(
    session: AsyncSession = Depends(get_session),
):
    """Get a featured exoplanet of the day with a fun fact.

    Picks a planet based on the current date and generates a fun fact
    from the planet's data.
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

    # Generate a data-driven fun fact
    facts = []
    if planet_response_obj.radius_earth > 0:
        facts.append(
            f"{planet_response_obj.name} has a radius of {planet_response_obj.radius_earth:.2f}× Earth"
        )
    if planet_response_obj.mass_earth is not None:
        facts.append(
            f"a mass of {planet_response_obj.mass_earth:.2f}× Earth"
        )
    if planet_response_obj.distance_light_years is not None:
        facts.append(
            f"and sits {planet_response_obj.distance_light_years:,.1f} light-years away from us"
        )
    if planet_response_obj.equilibrium_temperature_k is not None:
        facts.append(
            f"Its equilibrium temperature is about {planet_response_obj.equilibrium_temperature_k:.0f} K"
        )
    if planet_response_obj.habitable_zone:
        facts.append("— and it orbits within its star's habitable zone!")
    else:
        facts.append("— but it orbits outside the traditional habitable zone.")

    fun_fact = ", ".join(facts) if facts else (
        f"{planet_response_obj.name} was discovered in {planet_response_obj.discovery_year} "
        f"using the {planet_response_obj.discovery_method} method."
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
