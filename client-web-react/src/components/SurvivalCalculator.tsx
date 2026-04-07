import { useState } from 'react';
import type { Exoplanet, CalculateResponse } from '../types/exoplanet';
import { calculateSurvival } from '../api/client';

interface SurvivalCalculatorProps {
  planet: Exoplanet;
}

export default function SurvivalCalculator({ planet }: SurvivalCalculatorProps) {
  const [weight, setWeight] = useState<string>('70');
  const [results, setResults] = useState<CalculateResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCalculate = async () => {
    const userWeight = parseFloat(weight);
    if (isNaN(userWeight) || userWeight <= 0) {
      setError('Please enter a valid weight');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await calculateSurvival({
        planet_id: planet.id,
        user_weight_kg: userWeight,
      });
      setResults(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to calculate');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="survival-calculator">
      <h3>🧑‍🚀 Could You Survive There?</h3>

      <div className="calculator-input">
        <label>
          Your weight on Earth (kg):
          <input
            type="number"
            min="1"
            step="0.1"
            value={weight}
            onChange={(e) => setWeight(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleCalculate()}
          />
        </label>
        <button onClick={handleCalculate} disabled={loading} className="btn btn-primary">
          {loading ? 'Calculating...' : 'Calculate'}
        </button>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {loading && (
        <div className="calculation-results">
          <div className="skeleton skeleton-text" />
          <div className="skeleton skeleton-text" />
          <div className="skeleton skeleton-text" />
        </div>
      )}

      {results && !loading && (
        <div className="calculation-results">
          <div className="verdict-cards">
            <div className="verdict-card">
              <div className="verdict-icon">⚖️</div>
              <div className="verdict-content">
                <div className="verdict-label">Your Weight on {results.planet_name}</div>
                <div className="verdict-value">
                  {results.weight_on_planet_kg != null
                    ? `${results.weight_on_planet_kg.toFixed(1)} kg`
                    : 'N/A'}
                </div>
              </div>
            </div>

            <div className="verdict-card">
              <div className="verdict-icon">🌡️</div>
              <div className="verdict-content">
                <div className="verdict-label">Temperature</div>
                <div className="verdict-value">{results.temperature_verdict}</div>
              </div>
            </div>

            <div className="verdict-card">
              <div className="verdict-icon">🏋️</div>
              <div className="verdict-content">
                <div className="verdict-label">Gravity</div>
                <div className="verdict-value">{results.gravity_verdict}</div>
              </div>
            </div>

            {results.surface_gravity_ms2 != null && (
              <div className="verdict-card">
                <div className="verdict-icon">📐</div>
                <div className="verdict-content">
                  <div className="verdict-label">Surface Gravity</div>
                  <div className="verdict-value">{results.surface_gravity_ms2.toFixed(2)} m/s²</div>
                </div>
              </div>
            )}

            {results.escape_velocity_kms != null && (
              <div className="verdict-card">
                <div className="verdict-icon">🚀</div>
                <div className="verdict-content">
                  <div className="verdict-label">Escape Velocity</div>
                  <div className="verdict-value">{results.escape_velocity_kms.toFixed(2)} km/s</div>
                </div>
              </div>
            )}
          </div>

          <div className="travel-times">
            <h4>🛸 Travel Time to {results.planet_name}</h4>
            <div className="travel-time-grid">
              <div className="travel-time-item">
                <span className="travel-mode">🚶 Walking</span>
                <span className="travel-duration">{results.travel_time_walking}</span>
              </div>
              <div className="travel-time-item">
                <span className="travel-mode">🚗 Car</span>
                <span className="travel-duration">{results.travel_time_car}</span>
              </div>
              <div className="travel-time-item">
                <span className="travel-mode">✈️ Plane</span>
                <span className="travel-duration">{results.travel_time_plane}</span>
              </div>
              <div className="travel-time-item">
                <span className="travel-mode">🛰️ Voyager 1</span>
                <span className="travel-duration">{results.travel_time_voyager}</span>
              </div>
              <div className="travel-time-item">
                <span className="travel-mode">💡 Light</span>
                <span className="travel-duration">{results.travel_time_light}</span>
              </div>
              <div className="travel-time-item">
                <span className="travel-mode">📡 Radio Signal to Earth</span>
                <span className="travel-duration">{results.radio_signal_time_to_earth}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
