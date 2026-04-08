import type { Exoplanet } from '../types/exoplanet';
import PlanetVisual from './PlanetVisual';
import PlanetSizeCompare from './PlanetSizeCompare';

interface ComparisonModalProps {
  planetA: Exoplanet;
  planetB: Exoplanet;
  onClose: () => void;
}

export default function ComparisonModal({ planetA, planetB, onClose }: ComparisonModalProps) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content comparison-modal" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          ✕
        </button>

        <h2>🔬 Planet Comparison</h2>

        <div className="comparison-header">
          <div className="planet-select">
            <div className="planet-select-visual">
              <PlanetVisual
                radiusEarth={planetA.radius_earth}
                temperatureK={planetA.equilibrium_temperature_k}
                insolationFlux={planetA.insolation_flux}
                name={planetA.name}
                size={80}
                showLabel={false}
              />
            </div>
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
            <div className="planet-select-visual">
              <PlanetVisual
                radiusEarth={planetB.radius_earth}
                temperatureK={planetB.equilibrium_temperature_k}
                insolationFlux={planetB.insolation_flux}
                name={planetB.name}
                size={80}
                showLabel={false}
              />
            </div>
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

        {/* Size comparison with Earth for both planets */}
        <div className="comparison-size-comparison">
          <PlanetSizeCompare planet={planetA} maxSize={120} minSize={20} />
          <PlanetSizeCompare planet={planetB} maxSize={120} minSize={20} />
        </div>

        <ComparisonTable planetA={planetA} planetB={planetB} />
      </div>
    </div>
  );
}

function ComparisonTable({ planetA, planetB }: { planetA: Exoplanet; planetB: Exoplanet }) {
  const massA = planetA.mass_earth ?? 0;
  const massB = planetB.mass_earth ?? 0;
  const radiusA = planetA.radius_earth ?? 0;
  const radiusB = planetB.radius_earth ?? 0;
  const tempA = planetA.equilibrium_temperature_k;
  const tempB = planetB.equilibrium_temperature_k;
  const distA = planetA.distance_light_years;
  const distB = planetB.distance_light_years;
  const periodA = planetA.orbital_period_days;
  const periodB = planetB.orbital_period_days;

  // Density proxy: mass/radius³ (relative to Earth = 1)
  const densityA = radiusA > 0 ? massA / (radiusA ** 3) : null;
  const densityB = radiusB > 0 ? massB / (radiusB ** 3) : null;

  // Surface gravity proxy: mass/radius² (relative to Earth = 1)
  const gravityA = radiusA > 0 ? massA / (radiusA ** 2) : null;
  const gravityB = radiusB > 0 ? massB / (radiusB ** 2) : null;

  // Insolation verdict
  const insolationA = planetA.insolation_flux;
  const insolationB = planetB.insolation_flux;

  function insolationVerdict(val: number | null | undefined): string {
    if (val == null) return 'Unknown';
    if (val < 0.25) return '❄️ Too cold';
    if (val <= 1.1) return '🌍 Habitable';
    return '🔥 Too hot';
  }

  function formatRatio(val: number | null): string {
    if (val == null) return 'N/A';
    return `${val.toFixed(3)}×`;
  }

  function formatTemp(val: number | null | undefined): string {
    if (val == null) return 'N/A';
    return `${val} K`;
  }

  function formatDist(val: number | null | undefined): string {
    if (val == null) return 'N/A';
    return `${val.toFixed(1)} ly`;
  }

  function formatPeriod(val: number | null | undefined): string {
    if (val == null) return 'N/A';
    return `${val.toFixed(1)} days`;
  }

  return (
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
            <td>{radiusA > 0 ? `${radiusA.toFixed(3)}×` : 'N/A'}</td>
            <td>{radiusB > 0 ? `${radiusB.toFixed(3)}×` : 'N/A'}</td>
            <td>1.0×</td>
          </tr>
          <tr>
            <td>Mass</td>
            <td>{planetA.mass_earth != null ? `${massA.toFixed(3)}×${planetA.mass_estimated ? ' ≈' : ''}` : 'N/A'}</td>
            <td>{planetB.mass_earth != null ? `${massB.toFixed(3)}×${planetB.mass_estimated ? ' ≈' : ''}` : 'N/A'}</td>
            <td>1.0×</td>
          </tr>
          <tr>
            <td>Surface gravity</td>
            <td>{formatRatio(gravityA)}</td>
            <td>{formatRatio(gravityB)}</td>
            <td>1.0× (9.81 m/s²)</td>
          </tr>
          <tr>
            <td>Density proxy (M/R³)</td>
            <td>{formatRatio(densityA)}</td>
            <td>{formatRatio(densityB)}</td>
            <td>1.0× (5.51 g/cm³)</td>
          </tr>
          <tr>
            <td>Temperature</td>
            <td>{formatTemp(tempA)}</td>
            <td>{formatTemp(tempB)}</td>
            <td>~288 K</td>
          </tr>
          <tr>
            <td>Distance</td>
            <td>{formatDist(distA)}</td>
            <td>{formatDist(distB)}</td>
            <td>—</td>
          </tr>
          <tr>
            <td>Orbital Period</td>
            <td>{formatPeriod(periodA)}</td>
            <td>{formatPeriod(periodB)}</td>
            <td>365.25 days</td>
          </tr>
          <tr>
            <td>Insolation</td>
            <td>{insolationA != null ? `${insolationA.toFixed(3)}` : 'N/A'}</td>
            <td>{insolationB != null ? `${insolationB.toFixed(3)}` : 'N/A'}</td>
            <td>1.0</td>
          </tr>
          <tr>
            <td>Insolation verdict</td>
            <td>{insolationVerdict(insolationA)}</td>
            <td>{insolationVerdict(insolationB)}</td>
            <td>🌍 Habitable</td>
          </tr>
          <tr>
            <td>Discovery</td>
            <td>{planetA.discovery_year}</td>
            <td>{planetB.discovery_year}</td>
            <td>—</td>
          </tr>
          <tr>
            <td>Method</td>
            <td>{planetA.discovery_method || 'N/A'}</td>
            <td>{planetB.discovery_method || 'N/A'}</td>
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
  );
}
