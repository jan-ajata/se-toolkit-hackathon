"""Tests for the API endpoints using httpx AsyncClient with mocked DB."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import Depends

from exoplanet_explorer.main import create_app
from exoplanet_explorer.models.exoplanet import (
    ExoplanetResponse,
    ExoplanetListResponse,
    ExoplanetStats,
    CalculateResponse,
    PlanetOfDayResponse,
)
from exoplanet_explorer.database import get_session
from exoplanet_explorer.auth import verify_api_key


def _make_mock_planet(**overrides):
    """Create a mock exoplanet response."""
    defaults = {
        "id": 1,
        "name": "Kepler-442b",
        "hostname": "Kepler-442",
        "discovery_year": 2015,
        "discovery_method": "Transit",
        "radius_earth": 1.34,
        "mass_earth": 2.3,
        "mass_estimated": False,
        "orbital_period_days": 112.3,
        "equilibrium_temperature_k": 260.0,
        "distance_light_years": 1206.0,
        "semi_major_axis_au": 0.409,
        "insolation_flux": 0.57,
        "habitable_zone": True,
    }
    defaults.update(overrides)
    return ExoplanetResponse(**defaults)


@pytest.fixture
def client():
    """Create a test client with mocked dependencies."""
    app = create_app()

    # Override the API key dependency
    app.dependency_overrides[verify_api_key] = lambda: None

    # Create a mock session
    mock_session = MagicMock()

    def override_get_session():
        yield mock_session

    # Override the database session dependency
    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as test_client:
        yield test_client, mock_session

    # Clean up overrides
    app.dependency_overrides.clear()


class TestGetExoplanetsEndpoint:
    """Test GET /exoplanets/ endpoint."""

    def test_list_exoplanets(self, client):
        """Should return 200 with a list of planets."""
        test_client, mock_session = client

        mock_planet = _make_mock_planet()

        async def mock_read(*args, **kwargs):
            return ([mock_planet], 1)

        with patch(
            "exoplanet_explorer.routers.exoplanets.read_exoplanets",
            side_effect=mock_read,
        ):
            response = test_client.get("/exoplanets/")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Kepler-442b"

    def test_list_with_search_filter(self, client):
        """Should pass search param to DB function."""
        test_client, mock_session = client

        call_args = {}

        async def mock_read(*args, **kwargs):
            call_args.update(kwargs)
            return ([], 0)

        with patch(
            "exoplanet_explorer.routers.exoplanets.read_exoplanets",
            side_effect=mock_read,
        ):
            response = test_client.get("/exoplanets/?search=Kepler")

        assert response.status_code == 200
        assert call_args.get("search") == "Kepler"


class TestGetExoplanetEndpoint:
    """Test GET /exoplanets/{id} endpoint."""

    def test_get_exoplanet_detail(self, client):
        """Should return 200 with planet details."""
        test_client, mock_session = client

        mock_planet = _make_mock_planet()

        async def mock_read(*args, **kwargs):
            return mock_planet

        with patch(
            "exoplanet_explorer.routers.exoplanets.read_exoplanet",
            side_effect=mock_read,
        ):
            response = test_client.get("/exoplanets/1")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Kepler-442b"

    def test_get_nonexistent_planet(self, client):
        """Should return 404 for nonexistent planet."""
        test_client, mock_session = client

        async def mock_read(*args, **kwargs):
            return None

        with patch(
            "exoplanet_explorer.routers.exoplanets.read_exoplanet",
            side_effect=mock_read,
        ):
            response = test_client.get("/exoplanets/99999")

        assert response.status_code == 404


class TestGetExoplanetStats:
    """Test GET /exoplanets/stats endpoint."""

    def test_stats_endpoint(self, client):
        """Should return 200 with aggregate stats."""
        test_client, mock_session = client

        mock_stats = {
            "total_count": 100,
            "habitable_zone_count": 25,
            "average_radius_earth": 1.5,
            "closest_planet_name": "Proxima Centauri b",
            "closest_planet_distance_ly": 4.24,
            "detection_methods": {"Transit": 60, "Radial Velocity": 40},
        }

        async def mock_read(*args, **kwargs):
            return mock_stats

        with patch(
            "exoplanet_explorer.routers.exoplanets.read_exoplanet_stats",
            side_effect=mock_read,
        ):
            response = test_client.get("/exoplanets/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 100
        assert data["habitable_zone_count"] == 25


class TestCalculateEndpoint:
    """Test POST /exoplanets/calculate endpoint."""

    def test_calculate_survival(self, client):
        """Should return 200 with survival metrics."""
        test_client, mock_session = client

        mock_planet = _make_mock_planet()

        async def mock_read(*args, **kwargs):
            return mock_planet

        with patch(
            "exoplanet_explorer.routers.exoplanets.read_exoplanet",
            side_effect=mock_read,
        ):
            response = test_client.post(
                "/exoplanets/calculate",
                json={"planet_id": 1, "user_weight_kg": 70.0},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["planet_name"] == "Kepler-442b"
        assert "weight_on_planet_kg" in data
        assert "temperature_verdict" in data

    def test_calculate_missing_planet(self, client):
        """Should return 404 for nonexistent planet."""
        test_client, mock_session = client

        async def mock_read(*args, **kwargs):
            return None

        with patch(
            "exoplanet_explorer.routers.exoplanets.read_exoplanet",
            side_effect=mock_read,
        ):
            response = test_client.post(
                "/exoplanets/calculate",
                json={"planet_id": 99999, "user_weight_kg": 70.0},
            )

        assert response.status_code == 404


class TestCompareEndpoint:
    """Test POST /exoplanets/compare endpoint."""

    def test_compare_two_planets(self, client):
        """Should return 200 with numerical comparison and earth reference."""
        test_client, mock_session = client

        mock_planet_a = _make_mock_planet()
        mock_planet_b = _make_mock_planet(id=2, name="TRAPPIST-1e", radius_earth=0.92)

        call_count = 0

        async def mock_read(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return mock_planet_a
            return mock_planet_b

        with patch(
            "exoplanet_explorer.routers.exoplanets.read_exoplanet",
            side_effect=mock_read,
        ):
            response = test_client.post(
                "/exoplanets/compare",
                json={"planet_a_id": 1, "planet_b_id": 2},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["planet_a"]["name"] == "Kepler-442b"
        assert data["planet_b"]["name"] == "TRAPPIST-1e"
        assert "earth_reference" in data
        assert data["earth_reference"]["radius_earth"] == 1.0
        assert data["earth_reference"]["temperature_k"] == 288

    def test_compare_missing_planet_a(self, client):
        """Should return 404 if planet A doesn't exist."""
        test_client, mock_session = client

        async def mock_read(*args, **kwargs):
            return None

        with patch(
            "exoplanet_explorer.routers.exoplanets.read_exoplanet",
            side_effect=mock_read,
        ):
            response = test_client.post(
                "/exoplanets/compare",
                json={"planet_a_id": 99999, "planet_b_id": 2},
            )

        assert response.status_code == 404


class TestPlanetOfDayEndpoint:
    """Test GET /exoplanets/planet-of-the-day endpoint."""

    def test_planet_of_the_day(self, client):
        """Should return 200 with a planet and fun fact."""
        test_client, mock_session = client

        mock_planet = _make_mock_planet()

        async def mock_read(*args, **kwargs):
            return ([mock_planet], 1)

        with patch(
            "exoplanet_explorer.routers.exoplanets.read_exoplanets",
            side_effect=mock_read,
        ):
            response = test_client.get("/exoplanets/planet-of-the-day")

        assert response.status_code == 200
        data = response.json()
        assert "planet" in data
        assert "fun_fact" in data
        assert data["planet"]["name"] == "Kepler-442b"

    def test_planet_of_the_day_empty_catalog(self, client):
        """Should return 404 if no planets in catalog."""
        test_client, mock_session = client

        async def mock_read(*args, **kwargs):
            return ([], 0)

        with patch(
            "exoplanet_explorer.routers.exoplanets.read_exoplanets",
            side_effect=mock_read,
        ):
            response = test_client.get("/exoplanets/planet-of-the-day")

        assert response.status_code == 404
