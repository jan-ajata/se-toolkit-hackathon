"""Seed script: fetch exoplanet data from NASA Exoplanet Archive and insert into DB.

Run: python -m exoplanet_explorer.data.seed
"""

import asyncio
import csv
import io
import logging
import os
from urllib.parse import urlencode

import httpx
import asyncpg

logger = logging.getLogger(__name__)

# NASA Exoplanet Archive TAP API — free, no auth required
TAP_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"

# 1 Jupiter mass = 317.8 Earth masses
JUPITER_TO_EARTH_MASS = 317.8


def estimate_mass_earth(radius_earth: float) -> float:
    """Estimate planet mass in Earth masses from radius using piecewise power-law.

    Based on empirical mass-radius relationships from exoplanet data:
    - Rocky planets (R < 1.5 R⊕): M = R^3.7  (dense, iron/silicate)
    - Mini-Neptunes (1.5 <= R < 4.0 R⊕): M = R^2.3  (volatile-rich)
    - Gas giants (R >= 4.0 R⊕): M = R^1.7  (H/He dominated, compressible)

    References: Weiss & Marcy (2014), Chen & Kipping (2017).
    Coefficients tuned so Earth = 1 M⊕ at R = 1 R⊕, Jupiter ≈ 318 M⊕ at R ≈ 11.2 R⊕.
    """
    if radius_earth <= 0:
        return 0.0
    if radius_earth < 1.5:
        # Rocky/terrestrial regime
        return radius_earth ** 3.7
    elif radius_earth < 4.0:
        # Mini-Neptune / super-Earth regime
        return radius_earth ** 2.3
    else:
        # Gas giant regime
        return radius_earth ** 1.7


# Query: select notable fields from the planetary systems table
QUERY = """
SELECT pl_name, hostname, disc_year, discoverymethod,
       pl_rade, pl_bmasse, pl_orbper, pl_eqt, sy_dist,
       pl_orbsmax, pl_insol
FROM ps
WHERE default_flag = 1
  AND pl_rade IS NOT NULL
ORDER BY pl_name ASC
"""


def build_url() -> str:
    """Build the TAP API URL with our query."""
    params = {"query": QUERY, "format": "csv"}
    return f"{TAP_URL}?{urlencode(params)}"


async def fetch_exoplanets() -> list[dict]:
    """Fetch exoplanet data from NASA TAP API."""
    url = build_url()
    logger.info("Fetching exoplanet data from %s", url)

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.get(url)
        resp.raise_for_status()

    text = resp.text
    reader = csv.DictReader(io.StringIO(text))
    planets = []

    for row in reader:
        def _float(val: str | None) -> float | None:
            if val is None or val.strip() == "":
                return None
            try:
                return float(val)
            except (ValueError, TypeError):
                return None

        def _int(val: str | None) -> int:
            if val is None or val.strip() == "":
                return 0
            try:
                return int(float(val))
            except (ValueError, TypeError):
                return 0

        # pl_bmasse is in Jupiter masses; convert to Earth masses
        # 1 Jupiter mass = 317.8 Earth masses
        mass_jupiter = _float(row.get("pl_bmasse"))
        radius = _float(row.get("pl_rade")) or 0.0

        if mass_jupiter:
            mass_earth = mass_jupiter * JUPITER_TO_EARTH_MASS
        elif radius > 0:
            # No measured mass — estimate from radius using empirical M-R relationship
            mass_earth = estimate_mass_earth(radius)
        else:
            mass_earth = None

        planets.append({
            "name": row.get("pl_name", "").strip(),
            "hostname": row.get("hostname", "").strip(),
            "discovery_year": _int(row.get("disc_year")),
            "discovery_method": row.get("discoverymethod", "").strip(),
            "radius_earth": radius,
            "mass_earth": mass_earth,
            "mass_estimated": mass_jupiter is None and radius > 0,
            "orbital_period_days": _float(row.get("pl_orbper")) or 0.0,
            "equilibrium_temperature_k": _float(row.get("pl_eqt")),
            "distance_light_years": _float(row.get("sy_dist")),
            "semi_major_axis_au": _float(row.get("pl_orbsmax")),
            "insolation_flux": _float(row.get("pl_insol")),
        })

    logger.info("Fetched %d exoplanets", len(planets))
    return planets


async def seed_database() -> None:
    """Connect to PostgreSQL and insert exoplanet data."""
    db_host = os.environ.get("DB_HOST", "postgres")
    db_port = int(os.environ.get("DB_PORT", "5432"))
    db_name = os.environ.get("DB_NAME", "exoplanets")
    db_user = os.environ.get("DB_USER", "postgres")
    db_password = os.environ.get("DB_PASSWORD", "postgres")

    dsn = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    logger.info("Connecting to %s", dsn.replace(db_password, "****"))

    conn = await asyncpg.connect(dsn)
    try:
        # Create table if not exists
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS exoplanets (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                hostname VARCHAR(255) DEFAULT '',
                discovery_year INTEGER DEFAULT 0,
                discovery_method VARCHAR(100) DEFAULT '',
                radius_earth DOUBLE PRECISION DEFAULT 0.0,
                mass_earth DOUBLE PRECISION,
                mass_estimated BOOLEAN DEFAULT FALSE,
                orbital_period_days DOUBLE PRECISION DEFAULT 0.0,
                equilibrium_temperature_k DOUBLE PRECISION,
                distance_light_years DOUBLE PRECISION,
                semi_major_axis_au DOUBLE PRECISION,
                insolation_flux DOUBLE PRECISION,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)

        # Check if already seeded
        count = await conn.fetchval("SELECT COUNT(*) FROM exoplanets")
        if count > 0:
            logger.info("Database already has %d exoplanets, skipping seed", count)
            return

        planets = await fetch_exoplanets()

        # Insert using COPY for speed
        await conn.copy_records_to_table(
            "exoplanets",
            records=[
                (
                    p["name"],
                    p["hostname"],
                    p["discovery_year"],
                    p["discovery_method"],
                    p["radius_earth"],
                    p["mass_earth"],
                    p["mass_estimated"],
                    p["orbital_period_days"],
                    p["equilibrium_temperature_k"],
                    p["distance_light_years"],
                    p["semi_major_axis_au"],
                    p["insolation_flux"],
                )
                for p in planets
            ],
            columns=[
                "name", "hostname", "discovery_year", "discovery_method",
                "radius_earth", "mass_earth", "mass_estimated", "orbital_period_days",
                "equilibrium_temperature_k", "distance_light_years",
                "semi_major_axis_au", "insolation_flux",
            ],
        )

        logger.info("Successfully seeded %d exoplanets", len(planets))

    finally:
        await conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed_database())
