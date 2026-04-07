import { useState } from 'react';
import type { Exoplanet, CompareResponse } from '../types/exoplanet';
import { comparePlanets } from '../api/client';

interface ComparisonModalProps {
  planetA: Exoplanet;
  planetB: Exoplanet;
  onClose: () => void;
}

export default function ComparisonModal({ planetA, planetB, onClose }: ComparisonModalProps) {
  const [comparison, setComparison] = useState<CompareResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasCompared, setHasCompared] = useState(false);

  const handleCompare = async () => {
    setLoading(true);
    setError(null);
    setComparison(null);
    setHasCompared(true);

    try {
      const response = await comparePlanets({
        planet_a_id: planetA.id,
        planet_b_id: planetB.id,
      });
      setComparison(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to compare planets');
    } finally {
      setLoading(false);
    }
  };

  const formatValue = (value: number | null, suffix: string, multiplier = '× Earth'): string => {
    if (value == null) return 'N/A';
    return `${value.toFixed(2)} ${value === 1 ? '' : multiplier}`.replace(suffix, suffix).trim();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content comparison-modal" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          ✕
        </button>

        <h2>🔬 Planet Comparison</h2>

        <div className="comparison-header">
          <div className="planet-select">
            <h3>{planetA.name}</h3>
            <div className="planet-preview-stats">
              <div className="mini-stat">
                <span className="mini-stat-label">Radius:</span>
                <span className="mini-stat-value">
                  {planetA.radius_earth != null ? `${planetA.radius_earth.toFixed(2)}× Earth` : 'N/A'}
                </span>
              </div>
              <div className="mini-stat">
                <span className="mini-stat-label">Distance:</span>
                <span className="mini-stat-value">
                  {planetA.distance_light_years != null ? `${planetA.distance_light_years.toFixed(1)} ly` : 'N/A'}
                </span>
              </div>
              {planetA.habitable_zone && (
                <span className="badge badge-habitable">🌍 Habitable Zone</span>
              )}
            </div>
          </div>

          <div className="vs-divider">VS</div>

          <div className="planet-select">
            <h3>{planetB.name}</h3>
            <div className="planet-preview-stats">
              <div className="mini-stat">
                <span className="mini-stat-label">Radius:</span>
                <span className="mini-stat-value">
                  {planetB.radius_earth != null ? `${planetB.radius_earth.toFixed(2)}× Earth` : 'N/A'}
                </span>
              </div>
              <div className="mini-stat">
                <span className="mini-stat-label">Distance:</span>
                <span className="mini-stat-value">
                  {planetB.distance_light_years != null ? `${planetB.distance_light_years.toFixed(1)} ly` : 'N/A'}
                </span>
              </div>
              {planetB.habitable_zone && (
                <span className="badge badge-habitable">🌍 Habitable Zone</span>
              )}
            </div>
          </div>
        </div>

        {!hasCompared && (
          <div className="compare-action">
            <button onClick={handleCompare} className="btn btn-primary btn-large">
              🤖 Generate AI Comparison
            </button>
            <p className="compare-hint">
              Our AI will compare these two exoplanets in plain English
            </p>
          </div>
        )}

        {loading && (
          <div className="comparison-loading">
            <div className="skeleton skeleton-text" />
            <div className="skeleton skeleton-text" />
            <div className="skeleton skeleton-text" />
            <p className="loading-text">🤖 AI is analyzing these worlds...</p>
          </div>
        )}

        {error && <div className="error-banner">{error}</div>}

        {comparison && !loading && (
          <div className="comparison-result">
            <div className="comparison-text">
              <h4>AI Comparison</h4>
              <p>{comparison.comparison}</p>
            </div>

            <div className="side-by-side-stats">
              <h4>Side-by-Side Stats</h4>
              <table className="comparison-table">
                <thead>
                  <tr>
                    <th>Metric</th>
                    <th>{planetA.name}</th>
                    <th>{planetB.name}</th>
                    <th>Earth Reference</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Radius</td>
                    <td>{planetA.radius_earth != null ? `${planetA.radius_earth.toFixed(2)}×` : 'N/A'}</td>
                    <td>{planetB.radius_earth != null ? `${planetB.radius_earth.toFixed(2)}×` : 'N/A'}</td>
                    <td>1.0×</td>
                  </tr>
                  <tr>
                    <td>Mass</td>
                    <td>{planetA.mass_earth != null ? `${planetA.mass_earth.toFixed(2)}×` : 'N/A'}</td>
                    <td>{planetB.mass_earth != null ? `${planetB.mass_earth.toFixed(2)}×` : 'N/A'}</td>
                    <td>1.0×</td>
                  </tr>
                  <tr>
                    <td>Distance</td>
                    <td>{planetA.distance_light_years != null ? `${planetA.distance_light_years.toFixed(1)} ly` : 'N/A'}</td>
                    <td>{planetB.distance_light_years != null ? `${planetB.distance_light_years.toFixed(1)} ly` : 'N/A'}</td>
                    <td>—</td>
                  </tr>
                  <tr>
                    <td>Temperature</td>
                    <td>{planetA.equilibrium_temperature_k != null ? `${planetA.equilibrium_temperature_k} K` : 'N/A'}</td>
                    <td>{planetB.equilibrium_temperature_k != null ? `${planetB.equilibrium_temperature_k} K` : 'N/A'}</td>
                    <td>~288 K</td>
                  </tr>
                  <tr>
                    <td>Orbital Period</td>
                    <td>{planetA.orbital_period_days != null ? `${planetA.orbital_period_days.toFixed(1)} days` : 'N/A'}</td>
                    <td>{planetB.orbital_period_days != null ? `${planetB.orbital_period_days.toFixed(1)} days` : 'N/A'}</td>
                    <td>365.25 days</td>
                  </tr>
                  <tr>
                    <td>Discovery</td>
                    <td>{planetA.discovery_year}</td>
                    <td>{planetB.discovery_year}</td>
                    <td>—</td>
                  </tr>
                  <tr>
                    <td>Habitable Zone</td>
                    <td>{planetA.habitable_zone ? '✅ Yes' : '❌ No'}</td>
                    <td>{planetB.habitable_zone ? '✅ Yes' : '❌ No'}</td>
                    <td>✅ Yes</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
