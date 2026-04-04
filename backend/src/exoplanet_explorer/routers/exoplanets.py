"""Router for exoplanet endpoints."""

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
    ExoplanetListResponse,
    ExoplanetResponse,
    ExoplanetStats,
)

router = APIRouter()
logger = logging.getLogger(__name__)


def _to_response(record) -> ExoplanetResponse:
    """Convert DB record to API response, computing habitable zone flag."""
    insolation = record.insolation_flux
    habitable = (
        insolation is not None and 0.25 <= insolation <= 1.1
    )
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
        constellation=record.constellation,
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
    constellation: str | None = Query(None, description="Filter by constellation"),
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
            constellation=constellation,
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
