import type { Exoplanet } from '../types/exoplanet';

interface ExoplanetListProps {
  planets: Exoplanet[];
  loading: boolean;
  error: string | null;
  onSelectPlanet: (planet: Exoplanet) => void;
}

export default function ExoplanetList({ planets, loading, error, onSelectPlanet }: ExoplanetListProps) {
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
            <th>Name</th>
            <th>Discovery Year</th>
            <th>Radius (×Earth)</th>
            <th>Mass (×Earth)</th>
            <th>Distance (ly)</th>
            <th>Method</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {planets.map((planet) => (
            <tr key={planet.id} onClick={() => onSelectPlanet(planet)} className="planet-row">
              <td className="planet-name">{planet.name}</td>
              <td>{planet.discovery_year ?? 'N/A'}</td>
              <td>{planet.radius_earth?.toFixed(3) ?? 'N/A'}</td>
              <td>{planet.mass_earth?.toFixed(3) ?? 'N/A'}</td>
              <td>{planet.distance_light_years?.toFixed(1) ?? 'N/A'}</td>
              <td>{planet.discovery_method ?? 'N/A'}</td>
              <td>
                {planet.habitable_zone ? (
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
