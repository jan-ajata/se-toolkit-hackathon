"""SQLModel models for exoplanets."""

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class ExoplanetRecord(SQLModel, table=True):
    """A row in the exoplanets table."""

    __tablename__ = "exoplanets"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    hostname: str = ""
    discovery_year: int = 0
    discovery_method: str = ""
    radius_earth: float = 0.0
    mass_earth: float | None = None
    orbital_period_days: float = 0.0
    equilibrium_temperature_k: float | None = None
    distance_light_years: float | None = None
    semi_major_axis_au: float | None = None
    insolation_flux: float | None = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )


class ExoplanetResponse(SQLModel):
    """Schema returned by the API."""

    id: int
    name: str
    hostname: str
    discovery_year: int
    discovery_method: str
    radius_earth: float
    mass_earth: float | None
    orbital_period_days: float
    equilibrium_temperature_k: float | None
    distance_light_years: float | None
    semi_major_axis_au: float | None
    insolation_flux: float | None
    habitable_zone: bool


class ExoplanetListResponse(SQLModel):
    """Paginated list response."""

    items: list[ExoplanetResponse]
    total: int
    page: int
    page_size: int


class ExoplanetStats(SQLModel):
    """Aggregate statistics."""

    total_count: int
    habitable_zone_count: int
    average_radius_earth: float
    closest_planet_name: str
    closest_planet_distance_ly: float | None
    detection_methods: dict[str, int]


class CalculateRequest(SQLModel):
    """Request body for the calculator endpoint."""

    planet_id: int
    user_weight_kg: float = 70.0


class CalculateResponse(SQLModel):
    """Response from the calculator endpoint."""

    planet_name: str
    user_weight_kg: float
    weight_on_planet_kg: float | None
    surface_gravity_ms2: float | None
    travel_time_walking: str
    travel_time_car: str
    travel_time_plane: str
    travel_time_voyager: str
    travel_time_light: str
    temperature_verdict: str
    gravity_verdict: str
