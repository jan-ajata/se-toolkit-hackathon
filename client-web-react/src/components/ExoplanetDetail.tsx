import type { Exoplanet } from '../types/exoplanet';
import SurvivalCalculator from './SurvivalCalculator';

// Physical constants for conversion
const EARTH_RADIUS_KM = 6371;
const EARTH_MASS_KG = 5.972e24;

interface ExoplanetDetailProps {
  planet: Exoplanet;
  onClose: () => void;
  useRealValues: boolean;
}

export default function ExoplanetDetail({ planet, onClose, useRealValues }: ExoplanetDetailProps) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          ✕
        </button>

        <div className="detail-header">
          <h2>{planet.name}</h2>
          {planet.habitable_zone && <span className="badge badge-habitable">🌍 Habitable Zone</span>}
        </div>

        <div className="detail-stats">
          <div className="detail-stat">
            <span className="stat-icon">📅</span>
            <div>
              <div className="stat-label">Discovery Year</div>
              <div className="stat-value">{planet.discovery_year ?? 'N/A'}</div>
            </div>
          </div>
          <div className="detail-stat">
            <span className="stat-icon">🔭</span>
            <div>
              <div className="stat-label">Detection Method</div>
              <div className="stat-value">{planet.discovery_method ?? 'N/A'}</div>
            </div>
          </div>
          <div className="detail-stat">
            <span className="stat-icon">🌍</span>
            <div>
              <div className="stat-label">Radius</div>
              <div className="stat-value">
                {useRealValues
                  ? planet.radius_earth != null
                    ? `${(planet.radius_earth * EARTH_RADIUS_KM).toFixed(0)} km`
                    : 'N/A'
                  : planet.radius_earth != null
                    ? `${planet.radius_earth.toFixed(3)}× Earth`
                    : 'N/A'}
              </div>
            </div>
          </div>
          <div className="detail-stat">
            <span className="stat-icon">⚖️</span>
            <div>
              <div className="stat-label">Mass</div>
              <div className="stat-value">
                {useRealValues
                  ? planet.mass_earth != null
                    ? `${(planet.mass_earth * EARTH_MASS_KG).toExponential(2)} kg`
                    : 'N/A'
                  : planet.mass_earth != null
                    ? `${planet.mass_earth.toFixed(3)}× Earth`
                    : 'N/A'}
              </div>
            </div>
          </div>
          <div className="detail-stat">
            <span className="stat-icon">🌌</span>
            <div>
              <div className="stat-label">Distance</div>
              <div className="stat-value">
                {planet.distance_light_years != null
                  ? `${planet.distance_light_years.toFixed(1)} light years`
                  : 'N/A'}
              </div>
            </div>
          </div>
          <div className="detail-stat">
            <span className="stat-icon">🔄</span>
            <div>
              <div className="stat-label">Orbital Period</div>
              <div className="stat-value">
                {planet.orbital_period_days != null
                  ? `${planet.orbital_period_days.toFixed(1)} days`
                  : 'N/A'}
              </div>
            </div>
          </div>
          <div className="detail-stat">
            <span className="stat-icon">🌡️</span>
            <div>
              <div className="stat-label">Equilibrium Temp</div>
              <div className="stat-value">
                {planet.equilibrium_temperature_k != null
                  ? `${planet.equilibrium_temperature_k} K`
                  : 'N/A'}
              </div>
            </div>
          </div>
          {planet.semi_major_axis_au != null && (
            <div className="detail-stat">
              <span className="stat-icon">📏</span>
              <div>
                <div className="stat-label">Semi-Major Axis</div>
                <div className="stat-value">{planet.semi_major_axis_au.toFixed(3)} AU</div>
              </div>
            </div>
          )}
          {planet.insolation_flux != null && (
            <div className="detail-stat">
              <span className="stat-icon">☀️</span>
              <div>
                <div className="stat-label">Insolation Flux</div>
                <div className="stat-value">{planet.insolation_flux.toFixed(3)}</div>
              </div>
            </div>
          )}
          {planet.hostname && (
            <div className="detail-stat">
              <span className="stat-icon">⭐</span>
              <div>
                <div className="stat-label">Host Star</div>
                <div className="stat-value">{planet.hostname}</div>
              </div>
            </div>
          )}
        </div>

        <SurvivalCalculator planet={planet} />
      </div>
    </div>
  );
}
