import type { Exoplanet } from '../types/exoplanet';
import PlanetVisual from './PlanetVisual';

// Physical constants for conversion
const EARTH_RADIUS_KM = 6371;
const EARTH_MASS_KG = 5.972e24;

interface ExoplanetListProps {
  planets: Exoplanet[];
  loading: boolean;
  error: string | null;
  onSelectPlanet: (planet: Exoplanet) => void;
  useRealValues: boolean;
  compareMode?: boolean;
}

export default function ExoplanetList({ planets, loading, error, onSelectPlanet, useRealValues, compareMode = false }: ExoplanetListProps) {
  if (loading) {
    return (
      <div className="planet-list-loading">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="planet-row planet-row-skeleton">
            <div className="skeleton skeleton-text" />
            <div className="skeleton skeleton-text" />
            <div className="skeleton skeleton-text" />
            <div className="skeleton skeleton-text" />
            <div className="skeleton skeleton-text" />
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return <div className="error-banner">Failed to load planets: {error}</div>;
  }

  if (planets.length === 0) {
    return <div className="empty-state">No exoplanets found. Try adjusting your filters.</div>;
  }

  return (
    <div className="planet-list">
      <table className="planet-table">
        <thead>
          <tr>
            <th></th>
            <th>Name</th>
            <th>Discovery Year</th>
            <th>
              {useRealValues ? 'Radius (km)' : 'Radius (×Earth)'}
            </th>
            <th>
              {useRealValues ? 'Mass (kg)' : 'Mass (×Earth)'}
            </th>
            <th>Distance (ly)</th>
            <th>Method</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {planets.map((planet) => (
            <tr
              key={planet.id}
              onClick={() => onSelectPlanet(planet)}
              className={`planet-row ${compareMode ? 'compare-selectable' : ''}`}
            >
              <td className="planet-row-visual">
                <PlanetVisual
                  radiusEarth={planet.radius_earth}
                  temperatureK={planet.equilibrium_temperature_k}
                  insolationFlux={planet.insolation_flux}
                  name=""
                  size={32}
                  showLabel={false}
                />
              </td>
              <td className="planet-name">
                {compareMode && '🔬 '}
                {planet.name}
              </td>
              <td>{planet.discovery_year ?? 'N/A'}</td>
              <td>
                {useRealValues
                  ? planet.radius_earth != null
                    ? (planet.radius_earth * EARTH_RADIUS_KM).toFixed(0)
                    : 'N/A'
                  : planet.radius_earth?.toFixed(3) ?? 'N/A'}
              </td>
              <td>
                {useRealValues
                  ? planet.mass_earth != null
                    ? `${(planet.mass_earth * EARTH_MASS_KG).toExponential(2)}${planet.mass_estimated ? ' ≈' : ''}`
                    : 'N/A'
                  : planet.mass_earth != null
                    ? `${planet.mass_earth.toFixed(3)}${planet.mass_estimated ? ' ≈' : ''}`
                    : 'N/A'}
              </td>
              <td>{planet.distance_light_years?.toFixed(1) ?? 'N/A'}</td>
              <td>{planet.discovery_method ?? 'N/A'}</td>
              <td>
                {planet.insolation_flux != null && planet.insolation_flux >= 0.25 && planet.insolation_flux <= 1.1 ? (
                  <span className="badge badge-habitable">🌍 Habitable</span>
                ) : (
                  <span className="badge badge-hostile">🔥 Hostile</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
