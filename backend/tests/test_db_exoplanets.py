"""Tests for the exoplanet database layer using SQLite in-memory."""

import asyncio
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlmodel import SQLModel

from exoplanet_explorer.db.exoplanets import (
    read_exoplanets,
    read_exoplanet,
    read_exoplanet_stats,
)
from exoplanet_explorer.models.exoplanet import ExoplanetRecord


@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for the session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Create a fresh SQLite in-memory database for each test."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_maker() as session:
        # Insert test data
        test_planets = [
            ExoplanetRecord(
                name="Kepler-442b",
                hostname="Kepler-442",
                discovery_year=2015,
                discovery_method="Transit",
                radius_earth=1.34,
                mass_earth=2.3,
                orbital_period_days=112.3,
                equilibrium_temperature_k=260.0,
                distance_light_years=1206.0,
                semi_major_axis_au=0.409,
                insolation_flux=0.57,
                constellation="Lyra",
            ),
            ExoplanetRecord(
                name="Proxima Centauri b",
                hostname="Proxima Centauri",
                discovery_year=2016,
                discovery_method="Radial Velocity",
                radius_earth=1.03,
                mass_earth=1.27,
                orbital_period_days=11.2,
                equilibrium_temperature_k=234.0,
                distance_light_years=4.24,
                semi_major_axis_au=0.0485,
                insolation_flux=0.65,
                constellation="Centaurus",
            ),
            ExoplanetRecord(
                name="TRAPPIST-1e",
                hostname="TRAPPIST-1",
                discovery_year=2017,
                discovery_method="Transit",
                radius_earth=0.92,
                mass_earth=0.69,
                orbital_period_days=6.1,
                equilibrium_temperature_k=251.0,
                distance_light_years=40.7,
                semi_major_axis_au=0.029,
                insolation_flux=0.60,
                constellation="Aquarius",
            ),
        ]
        session.add_all(test_planets)
        await session.commit()

    yield session_maker

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


class TestReadExoplanets:
    """Test the read_exoplanets function."""

    @pytest.mark.asyncio
    async def test_read_all(self, db_session):
        """Should return all planets when no filters."""
        async with db_session() as session:
            items, total = await read_exoplanets(session)
        assert total == 3
        assert len(items) == 3

    @pytest.mark.asyncio
    async def test_pagination(self, db_session):
        """Should respect page and page_size."""
        async with db_session() as session:
            items, total = await read_exoplanets(session, page=1, page_size=2)
        assert total == 3
        assert len(items) == 2

    @pytest.mark.asyncio
    async def test_search_by_name(self, db_session):
        """Should filter by name substring."""
        async with db_session() as session:
            items, total = await read_exoplanets(session, search="Kepler")
        assert total == 1
        assert items[0].name == "Kepler-442b"

    @pytest.mark.asyncio
    async def test_habitable_zone_filter(self, db_session):
        """Should filter by habitable zone (insolation_flux between 0.25 and 1.1)."""
        async with db_session() as session:
            items, total = await read_exoplanets(session, habitable_zone=True)
        # All 3 planets have insolation_flux in habitable range
        assert total == 3

    @pytest.mark.asyncio
    async def test_radius_filter(self, db_session):
        """Should filter by min/max radius."""
        async with db_session() as session:
            items, total = await read_exoplanets(session, min_radius=1.0, max_radius=1.5)
        assert total == 2  # Kepler-442b and Proxima Centauri b

    @pytest.mark.asyncio
    async def test_constellation_filter(self, db_session):
        """Should filter by constellation."""
        async with db_session() as session:
            items, total = await read_exoplanets(session, constellation="Lyra")
        assert total == 1
        assert items[0].constellation == "Lyra"


class TestReadExoplanet:
    """Test the read_exoplanet function."""

    @pytest.mark.asyncio
    async def test_read_by_id(self, db_session):
        """Should return a planet by ID."""
        async with db_session() as session:
            items, _ = await read_exoplanets(session, search="Kepler-442b")
            planet_id = items[0].id

        async with db_session() as session:
            planet = await read_exoplanet(session, planet_id)

        assert planet is not None
        assert planet.name == "Kepler-442b"

    @pytest.mark.asyncio
    async def test_read_nonexistent_id(self, db_session):
        """Should return None for nonexistent ID."""
        async with db_session() as session:
            planet = await read_exoplanet(session, 99999)
        assert planet is None


class TestReadExoplanetStats:
    """Test the read_exoplanet_stats function."""

    @pytest.mark.asyncio
    async def test_stats_total_count(self, db_session):
        """Should return correct total count."""
        async with db_session() as session:
            stats = await read_exoplanet_stats(session)
        assert stats["total_count"] == 3

    @pytest.mark.asyncio
    async def test_stats_habitable_count(self, db_session):
        """Should count habitable zone planets."""
        async with db_session() as session:
            stats = await read_exoplanet_stats(session)
        assert stats["habitable_count"] == 3

    @pytest.mark.asyncio
    async def test_stats_closest_planet(self, db_session):
        """Should find the closest planet (Proxima Centauri b at 4.24 ly)."""
        async with db_session() as session:
            stats = await read_exoplanet_stats(session)
        assert stats["closest_planet_name"] == "Proxima Centauri b"
        assert stats["closest_planet_distance_ly"] == pytest.approx(4.24)

    @pytest.mark.asyncio
    async def test_stats_detection_methods(self, db_session):
        """Should return detection method breakdown."""
        async with db_session() as session:
            stats = await read_exoplanet_stats(session)
        assert "Transit" in stats["detection_methods"]
        assert "Radial Velocity" in stats["detection_methods"]
        assert stats["detection_methods"]["Transit"] == 2
        assert stats["detection_methods"]["Radial Velocity"] == 1
