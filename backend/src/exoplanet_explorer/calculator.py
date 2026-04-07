"""Survival metrics calculator for exoplanets.

Pure math — no external dependencies or API calls.
"""

import math

# Physical constants
G = 6.67430e-11  # Gravitational constant, m³/(kg·s²)
EARTH_MASS_KG = 5.972e24
EARTH_RADIUS_M = 6.371e6
EARTH_GRAVITY = 9.80665  # m/s²
LY_IN_KM = 9.461e12

# Speed constants (km/h)
WALKING_SPEED = 5
CAR_SPEED = 100
PLANE_SPEED = 900
VOYAGER_SPEED = 61_000
SPEED_OF_LIGHT_KMH = 1_079_252_848.8  # ~299,792 km/s


def _format_duration(hours: float) -> str:
    """Format hours into a human-readable string."""
    if hours < 1:
        return f"{hours * 60:.0f} minutes"
    if hours < 24:
        return f"{hours:.1f} hours"
    days = hours / 24
    if days < 365:
        return f"{days:.0f} days"
    years = days / 365.25
    if years < 1_000_000:
        return f"{years:,.0f} years"
    return f"{years:,.0e} years"


def calculate_weight_on_planet(
    user_weight_kg: float,
    planet_mass_earth: float | None,
    planet_radius_earth: float,
) -> float | None:
    """Calculate user's weight on the planet in kg-equivalent.

    Uses: weight = weight_earth × (planet_mass / earth_mass) / (planet_radius / earth_radius)²
    """
    if planet_mass_earth is None or planet_mass_earth <= 0:
        return None
    if planet_radius_earth <= 0:
        return None
    return user_weight_kg * planet_mass_earth / (planet_radius_earth ** 2)


def calculate_surface_gravity(
    planet_mass_earth: float | None,
    planet_radius_earth: float,
) -> float | None:
    """Calculate surface gravity in m/s²."""
    if planet_mass_earth is None or planet_mass_earth <= 0:
        return None
    if planet_radius_earth <= 0:
        return None
    mass_kg = planet_mass_earth * EARTH_MASS_KG
    radius_m = planet_radius_earth * EARTH_RADIUS_M
    return G * mass_kg / (radius_m ** 2)


def calculate_escape_velocity(
    planet_mass_earth: float | None,
    planet_radius_earth: float,
) -> float | None:
    """Calculate escape velocity in km/s.

    Formula: v_escape = sqrt(2 * G * M / R)
    """
    if planet_mass_earth is None or planet_mass_earth <= 0:
        return None
    if planet_radius_earth <= 0:
        return None
    mass_kg = planet_mass_earth * EARTH_MASS_KG
    radius_m = planet_radius_earth * EARTH_RADIUS_M
    v_escape_ms = math.sqrt(2 * G * mass_kg / radius_m)
    return v_escape_ms / 1000  # Convert to km/s


def calculate_radio_signal_time(
    distance_light_years: float | None,
) -> str:
    """Calculate how long a radio signal would take to reach Earth.

    Radio waves travel at the speed of light, so time = distance in years.
    """
    if distance_light_years is None or distance_light_years <= 0:
        return "Unknown"
    # Format with appropriate units
    if distance_light_years < 1:
        days = distance_light_years * 365.25
        return f"{days:.1f} days"
    if distance_light_years < 1000:
        return f"{distance_light_years:,.1f} years"
    return f"{distance_light_years:,.0f} years"


def calculate_travel_time(
    distance_light_years: float | None,
    speed_kmh: float,
) -> str:
    """Calculate travel time at given speed."""
    if distance_light_years is None or distance_light_years <= 0:
        return "Unknown"
    distance_km = distance_light_years * LY_IN_KM
    hours = distance_km / speed_kmh
    return _format_duration(hours)


def get_temperature_verdict(temperature_k: float | None) -> str:
    """Return a human-readable temperature verdict."""
    if temperature_k is None:
        return "🤷 Unknown"
    if temperature_k < 200:
        return "🥶 You'd freeze instantly"
    if temperature_k < 273:
        return "❄️ Freezing but survivable"
    if temperature_k <= 320:
        return "🌡️ Temperate — comfortable!"
    if temperature_k <= 500:
        return "🔥 Very hot"
    return "💀 You'd burn up"


def get_gravity_verdict(gravity_ms2: float | None) -> str:
    """Return a human-readable gravity verdict."""
    if gravity_ms2 is None:
        return "🤷 Unknown"
    g_ratio = gravity_ms2 / EARTH_GRAVITY
    if g_ratio < 0.5:
        return "🪶 You'd feel light as a feather"
    if g_ratio <= 2:
        return "👍 Manageable"
    if g_ratio <= 4:
        return "😰 Very heavy"
    return "💀 Crushing weight"


def calculate_survival_metrics(
    planet_name: str,
    user_weight_kg: float,
    planet_mass_earth: float | None,
    planet_radius_earth: float,
    distance_light_years: float | None,
    temperature_k: float | None,
) -> dict:
    """Calculate all survival metrics for a given planet."""
    weight_on_planet = calculate_weight_on_planet(
        user_weight_kg, planet_mass_earth, planet_radius_earth
    )
    surface_gravity = calculate_surface_gravity(
        planet_mass_earth, planet_radius_earth
    )
    escape_velocity = calculate_escape_velocity(
        planet_mass_earth, planet_radius_earth
    )

    return {
        "planet_name": planet_name,
        "user_weight_kg": user_weight_kg,
        "weight_on_planet_kg": round(weight_on_planet, 2) if weight_on_planet is not None else None,
        "surface_gravity_ms2": round(surface_gravity, 3) if surface_gravity is not None else None,
        "escape_velocity_kms": round(escape_velocity, 3) if escape_velocity is not None else None,
        "travel_time_walking": calculate_travel_time(distance_light_years, WALKING_SPEED),
        "travel_time_car": calculate_travel_time(distance_light_years, CAR_SPEED),
        "travel_time_plane": calculate_travel_time(distance_light_years, PLANE_SPEED),
        "travel_time_voyager": calculate_travel_time(distance_light_years, VOYAGER_SPEED),
        "travel_time_light": f"{distance_light_years:,.1f} years" if distance_light_years else "Unknown",
        "radio_signal_time_to_earth": calculate_radio_signal_time(distance_light_years),
        "temperature_verdict": get_temperature_verdict(temperature_k),
        "gravity_verdict": get_gravity_verdict(surface_gravity),
    }
