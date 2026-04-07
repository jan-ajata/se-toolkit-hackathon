"""Database operations for exoplanets."""

import logging

from sqlalchemy import func, or_
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from exoplanet_explorer.models.exoplanet import ExoplanetRecord

logger = logging.getLogger(__name__)


async def read_exoplanets(
    session: AsyncSession,
    search: str | None = None,
    min_radius: float | None = None,
    max_radius: float | None = None,
    min_mass: float | None = None,
    max_mass: float | None = None,
    habitable_zone: bool | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[ExoplanetRecord], int]:
    """Read exoplanets with optional filters. Returns (items, total_count)."""
    query = select(ExoplanetRecord)
    count_query = select(func.count(ExoplanetRecord.id))

    if search:
        filter_cond = ExoplanetRecord.name.ilike(f"%{search}%")
        query = query.where(filter_cond)
        count_query = count_query.where(filter_cond)

    if min_radius is not None:
        query = query.where(ExoplanetRecord.radius_earth >= min_radius)
        count_query = count_query.where(ExoplanetRecord.radius_earth >= min_radius)

    if max_radius is not None:
        query = query.where(ExoplanetRecord.radius_earth <= max_radius)
        count_query = count_query.where(ExoplanetRecord.radius_earth <= max_radius)

    if min_mass is not None:
        query = query.where(ExoplanetRecord.mass_earth >= min_mass)
        count_query = count_query.where(ExoplanetRecord.mass_earth >= min_mass)

    if max_mass is not None:
        query = query.where(ExoplanetRecord.mass_earth <= max_mass)
        count_query = count_query.where(ExoplanetRecord.mass_earth <= max_mass)

    if habitable_zone is not None:
        if habitable_zone:
            query = query.where(
                ExoplanetRecord.insolation_flux.between(0.25, 1.1)
            )
            count_query = count_query.where(
                ExoplanetRecord.insolation_flux.between(0.25, 1.1)
            )
        else:
            query = query.where(
                or_(
                    ExoplanetRecord.insolation_flux < 0.25,
                    ExoplanetRecord.insolation_flux > 1.1,
                    ExoplanetRecord.insolation_flux.is_(None),
                )
            )
            count_query = count_query.where(
                or_(
                    ExoplanetRecord.insolation_flux < 0.25,
                    ExoplanetRecord.insolation_flux > 1.1,
                    ExoplanetRecord.insolation_flux.is_(None),
                )
            )

    result = await session.exec(count_query)
    total = result.one()

    query = query.offset((page - 1) * page_size).limit(page_size).order_by(
        ExoplanetRecord.name
    )

    logger.info(
        "db_query",
        extra={
            "event": "db_query",
            "table": "exoplanets",
            "operation": "select",
            "page": page,
            "page_size": page_size,
        },
    )
    result = await session.exec(query)
    return list(result.all()), total


async def read_exoplanet(session: AsyncSession, planet_id: int) -> ExoplanetRecord | None:
    """Read a single exoplanet by id."""
    return await session.get(ExoplanetRecord, planet_id)


async def read_exoplanet_stats(session: AsyncSession) -> dict:
    """Read aggregate statistics about the exoplanet catalog."""
    # Total count
    total_result = await session.exec(select(func.count(ExoplanetRecord.id)))
    total_count = total_result.one()

    # Habitable zone count
    hz_result = await session.exec(
        select(func.count(ExoplanetRecord.id)).where(
            ExoplanetRecord.insolation_flux.between(0.25, 1.1)
        )
    )
    habitable_count = hz_result.one()

    # Average radius
    avg_result = await session.exec(
        select(func.avg(ExoplanetRecord.radius_earth))
    )
    avg_radius = avg_result.one() or 0.0

    # Closest planet
    closest_result = await session.exec(
        select(ExoplanetRecord)
        .where(ExoplanetRecord.distance_light_years.isnot(None))
        .order_by(ExoplanetRecord.distance_light_years.asc())
        .limit(1)
    )
    closest = closest_result.first()

    # Detection method breakdown
    method_result = await session.exec(
        select(ExoplanetRecord.discovery_method, func.count(ExoplanetRecord.id))
        .where(ExoplanetRecord.discovery_method != "")
        .group_by(ExoplanetRecord.discovery_method)
    )
    detection_methods = dict(method_result.all())

    return {
        "total_count": total_count,
        "habitable_zone_count": habitable_count,
        "average_radius_earth": round(avg_radius, 2),
        "closest_planet_name": closest.name if closest else "Unknown",
        "closest_planet_distance_ly": closest.distance_light_years if closest else None,
        "detection_methods": detection_methods,
    }
