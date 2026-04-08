import { useState, useEffect } from 'react';
import type { PlanetOfDayResponse } from '../types/exoplanet';
import { getPlanetOfDay } from '../api/client';
import PlanetVisual from './PlanetVisual';

interface PlanetOfDayProps {
  onExplorePlanet: (id: number) => void;
}

export default function PlanetOfDay({ onExplorePlanet }: PlanetOfDayProps) {
  const [data, setData] = useState<PlanetOfDayResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    getPlanetOfDay()
      .then((result) => {
        if (!cancelled) {
          setData(result);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load planet of the day');
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return (
      <div className="planet-of-the-day">
        <div className="potd-header">
          <h3>🌟 Planet of the Day</h3>
        </div>
        <div className="potd-content">
          <div className="skeleton skeleton-planet" />
          <div className="skeleton skeleton-text" />
          <div className="skeleton skeleton-text" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="planet-of-the-day">
        <div className="potd-header">
          <h3>🌟 Planet of the Day</h3>
        </div>
        <div className="error-banner">{error}</div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  const { planet, fun_fact } = data;

  return (
    <div className="planet-of-the-day">
      <div className="potd-header">
        <h3>🌟 Planet of the Day</h3>
        {planet.habitable_zone && (
          <span className="badge badge-habitable">🌍 Habitable Zone</span>
        )}
      </div>

      <div className="potd-planet-info">
        <div className="potd-planet-info-row">
          <PlanetVisual
            radiusEarth={planet.radius_earth}
            temperatureK={planet.equilibrium_temperature_k}
            insolationFlux={planet.insolation_flux}
            name=""
            size={60}
            showLabel={false}
          />
          <div className="potd-planet-info-text">
            <h4 className="potd-planet-name">{planet.name}</h4>
            <div className="potd-quick-stats">
              {planet.radius_earth != null && (
                <span className="quick-stat">
                  <span className="stat-icon">🌍</span>
                  <span>{planet.radius_earth.toFixed(2)}× Earth radius</span>
                </span>
              )}
              {planet.distance_light_years != null && (
                <span className="quick-stat">
                  <span className="stat-icon">🌌</span>
                  <span>{planet.distance_light_years.toFixed(1)} ly away</span>
                </span>
              )}
              {planet.discovery_year != null && (
                <span className="quick-stat">
                  <span className="stat-icon">📅</span>
                  <span>Discovered {planet.discovery_year}</span>
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="potd-fun-fact">
        <div className="fun-fact-label">💡 Did you know?</div>
        <p>{fun_fact}</p>
      </div>

      <button
        className="btn btn-primary btn-explore"
        onClick={() => onExplorePlanet(planet.id)}
      >
        🔭 Explore This Planet
      </button>
    </div>
  );
}
