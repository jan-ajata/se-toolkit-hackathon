"""Tests for the survival metrics calculator."""

import pytest
from exoplanet_explorer.calculator import (
    calculate_weight_on_planet,
    calculate_surface_gravity,
    calculate_escape_velocity,
    calculate_radio_signal_time,
    calculate_travel_time,
    get_temperature_verdict,
    get_gravity_verdict,
    calculate_survival_metrics,
    EARTH_GRAVITY,
)


class TestCalculateWeightOnPlanet:
    """Test weight calculation on different planets."""

    def test_earth_weight_stays_same(self):
        """On Earth (mass=1, radius=1), weight should stay the same."""
        assert calculate_weight_on_planet(70.0, 1.0, 1.0) == pytest.approx(70.0)

    def test_double_mass_double_radius(self):
        """Double mass, double radius → weight = 70 * 2 / 4 = 35."""
        assert calculate_weight_on_planet(70.0, 2.0, 2.0) == pytest.approx(35.0)

    def test_mars_like_planet(self):
        """Mars: ~0.107 Earth mass, ~0.532 Earth radius."""
        weight = calculate_weight_on_planet(70.0, 0.107, 0.532)
        assert weight == pytest.approx(26.5, abs=0.5)

    def test_none_mass_returns_none(self):
        """If mass is None, should return None."""
        assert calculate_weight_on_planet(70.0, None, 1.0) is None

    def test_zero_mass_returns_none(self):
        """Zero mass should return None."""
        assert calculate_weight_on_planet(70.0, 0.0, 1.0) is None

    def test_zero_radius_returns_none(self):
        """Zero radius should return None."""
        assert calculate_weight_on_planet(70.0, 1.0, 0.0) is None

    def test_jupiter_heavy(self):
        """Jupiter: ~317.8 Earth mass, ~11.2 Earth radius → very heavy."""
        weight = calculate_weight_on_planet(70.0, 317.8, 11.2)
        assert weight == pytest.approx(177.0, abs=1.0)


class TestCalculateSurfaceGravity:
    """Test surface gravity calculation."""

    def test_earth_gravity(self):
        """Earth should return ~9.81 m/s²."""
        gravity = calculate_surface_gravity(1.0, 1.0)
        assert gravity == pytest.approx(EARTH_GRAVITY, rel=0.01)

    def test_mars_gravity(self):
        """Mars: ~0.107 mass, ~0.532 radius → ~3.7 m/s²."""
        gravity = calculate_surface_gravity(0.107, 0.532)
        assert gravity == pytest.approx(3.7, abs=0.2)

    def test_none_mass_returns_none(self):
        assert calculate_surface_gravity(None, 1.0) is None

    def test_zero_radius_returns_none(self):
        assert calculate_surface_gravity(1.0, 0.0) is None


class TestCalculateTravelTime:
    """Test travel time calculations."""

    def test_unknown_distance(self):
        """None distance should return 'Unknown'."""
        assert calculate_travel_time(None, 100) == "Unknown"

    def test_zero_distance(self):
        """Zero distance should return 'Unknown'."""
        assert calculate_travel_time(0.0, 100) == "Unknown"

    def test_light_travel_time(self):
        """At speed of light, 1 ly should take 1 year."""
        # Speed of light in km/h
        result = calculate_travel_time(1.0, 1_079_252_848.8)
        assert "years" in result
        assert "1" in result

    def test_walking_very_slow(self):
        """Walking 1 ly should take millions of years."""
        result = calculate_travel_time(1.0, 5)
        assert "years" in result


class TestGetTemperatureVerdict:
    """Test temperature verdicts."""

    def test_freezing(self):
        assert "freeze" in get_temperature_verdict(150)

    def test_cold(self):
        assert "Freezing" in get_temperature_verdict(250)

    def test_temperate(self):
        assert "comfortable" in get_temperature_verdict(290)

    def test_hot(self):
        assert "hot" in get_temperature_verdict(400)

    def test_burning(self):
        assert "burn" in get_temperature_verdict(600)

    def test_none_unknown(self):
        assert "Unknown" in get_temperature_verdict(None)


class TestGetGravityVerdict:
    """Test gravity verdicts."""

    def test_earth_like(self):
        """Earth gravity should be 'Manageable'."""
        verdict = get_gravity_verdict(9.81)
        assert "Manageable" in verdict

    def test_low_gravity(self):
        verdict = get_gravity_verdict(2.0)
        assert "light" in verdict.lower()

    def test_high_gravity(self):
        verdict = get_gravity_verdict(30.0)
        assert "heavy" in verdict.lower() or "Crushing" in verdict

    def test_none_unknown(self):
        assert "Unknown" in get_gravity_verdict(None)


class TestCalculateSurvivalMetrics:
    """Test the combined survival metrics calculator."""

    def test_earth_like_planet(self):
        """Earth-like planet should have reasonable metrics."""
        metrics = calculate_survival_metrics(
            planet_name="Earth 2.0",
            user_weight_kg=70.0,
            planet_mass_earth=1.0,
            planet_radius_earth=1.0,
            distance_light_years=100.0,
            temperature_k=288.0,
        )

        assert metrics["planet_name"] == "Earth 2.0"
        assert metrics["user_weight_kg"] == 70.0
        assert metrics["weight_on_planet_kg"] == pytest.approx(70.0)
        assert "comfortable" in metrics["temperature_verdict"].lower()
        assert "Manageable" in metrics["gravity_verdict"]

    def test_missing_mass(self):
        """Planet with no mass data should return None for weight."""
        metrics = calculate_survival_metrics(
            planet_name="Unknown",
            user_weight_kg=70.0,
            planet_mass_earth=None,
            planet_radius_earth=1.5,
            distance_light_years=50.0,
            temperature_k=None,
        )

        assert metrics["weight_on_planet_kg"] is None
        assert metrics["surface_gravity_ms2"] is None
        assert "Unknown" in metrics["temperature_verdict"]


class TestCalculateEscapeVelocity:
    """Test escape velocity calculation."""

    def test_earth_escape_velocity(self):
        """Earth escape velocity is ~11.2 km/s."""
        v_escape = calculate_escape_velocity(1.0, 1.0)
        assert v_escape == pytest.approx(11.2, abs=0.2)

    def test_mars_escape_velocity(self):
        """Mars: ~0.107 mass, ~0.532 radius → ~5.0 km/s."""
        v_escape = calculate_escape_velocity(0.107, 0.532)
        assert v_escape == pytest.approx(5.0, abs=0.3)

    def test_jupiter_escape_velocity(self):
        """Jupiter: ~317.8 mass, ~11.2 radius → ~59.5 km/s."""
        v_escape = calculate_escape_velocity(317.8, 11.2)
        assert v_escape == pytest.approx(59.5, abs=1.0)

    def test_none_mass_returns_none(self):
        assert calculate_escape_velocity(None, 1.0) is None

    def test_zero_radius_returns_none(self):
        assert calculate_escape_velocity(1.0, 0.0) is None


class TestCalculateRadioSignalTime:
    """Test radio signal travel time calculation."""

    def test_unknown_distance(self):
        """None distance should return 'Unknown'."""
        assert calculate_radio_signal_time(None) == "Unknown"

    def test_zero_distance(self):
        """Zero distance should return 'Unknown'."""
        assert calculate_radio_signal_time(0.0) == "Unknown"

    def test_one_light_year(self):
        """1 ly should take 1 year for radio signal."""
        result = calculate_radio_signal_time(1.0)
        assert "1.0" in result and "year" in result

    def test_sub_light_year(self):
        """0.5 ly should return days."""
        result = calculate_radio_signal_time(0.5)
        assert "days" in result

    def test_large_distance(self):
        """1000 ly should return rounded years."""
        result = calculate_radio_signal_time(1000.0)
        assert "1,000" in result and "year" in result

    def test_small_distance(self):
        """100 ly should return rounded years."""
        result = calculate_radio_signal_time(100.0)
        assert "100.0" in result and "year" in result
