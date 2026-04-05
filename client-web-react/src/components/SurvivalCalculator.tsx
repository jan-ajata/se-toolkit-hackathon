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
                <div className="verdict-value">{results.temperature_verdict ?? 'N/A'}</div>
              </div>
            </div>

            <div className="verdict-card">
              <div className="verdict-icon">🏋️</div>
              <div className="verdict-content">
                <div className="verdict-label">Gravity</div>
                <div className="verdict-value">{results.gravity_verdict ?? 'N/A'}</div>
              </div>
            </div>

            {results.surface_gravity_m_s2 != null && (
              <div className="verdict-card">
                <div className="verdict-icon">📐</div>
                <div className="verdict-content">
                  <div className="verdict-label">Surface Gravity</div>
                  <div className="verdict-value">{results.surface_gravity_m_s2.toFixed(2)} m/s²</div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
