import { useState, useEffect, useCallback } from 'react';
import type { Exoplanet, ExoplanetFilters, ExoplanetStats } from './types/exoplanet';
import { getExoplanets, getExoplanetStats } from './api/client';
import StatsCards from './components/StatsCards';
import FilterPanel from './components/FilterPanel';
import ExoplanetList from './components/ExoplanetList';
import ExoplanetDetail from './components/ExoplanetDetail';
import './App.css';

export default function App() {
  const [planets, setPlanets] = useState<Exoplanet[]>([]);
  const [total, setTotal] = useState(0);
  const [stats, setStats] = useState<ExoplanetStats | null>(null);
  const [selectedPlanet, setSelectedPlanet] = useState<Exoplanet | null>(null);
  const [useRealValues, setUseRealValues] = useState(false);

  const [filters, setFilters] = useState<ExoplanetFilters>({ page: 1, page_size: 20 });
  const [loading, setLoading] = useState(true);
  const [statsLoading, setStatsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statsError, setStatsError] = useState<string | null>(null);

  // Fetch stats
  useEffect(() => {
    let cancelled = false;
    setStatsLoading(true);
    setStatsError(null);

    getExoplanetStats()
      .then((data: ExoplanetStats) => {
        if (!cancelled) {
          setStats(data);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setStatsError(err instanceof Error ? err.message : 'Failed to load stats');
        }
      })
      .finally(() => {
        if (!cancelled) {
          setStatsLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  // Fetch planets
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    getExoplanets(filters)
      .then((data) => {
        if (!cancelled) {
          setPlanets(data.items);
          setTotal(data.total);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load planets');
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
  }, [filters]);

  const handleFilterChange = useCallback((newFilters: ExoplanetFilters) => {
    setFilters(newFilters);
  }, []);

  const handleSelectPlanet = useCallback((planet: Exoplanet) => {
    setSelectedPlanet(planet);
  }, []);

  const handleCloseDetail = useCallback(() => {
    setSelectedPlanet(null);
  }, []);

  const handlePageChange = useCallback(
    (delta: number) => {
      const newPage = (filters.page ?? 1) + delta;
      if (newPage >= 1) {
        setFilters({ ...filters, page: newPage });
      }
    },
    [filters]
  );

  const totalPages = Math.ceil(total / (filters.page_size ?? 20));
  const currentPage = filters.page ?? 1;

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🪐 Exoplanet Explorer</h1>
          <p className="app-subtitle">
            Browse, filter, and calculate survival metrics for confirmed exoplanets
          </p>
        </div>
      </header>

      <main className="app-main">
        <div className="toolbar">
          <StatsCards stats={stats} loading={statsLoading} error={statsError} />
          <label className="toggle-unit">
            <input
              type="checkbox"
              checked={useRealValues}
              onChange={(e) => setUseRealValues(e.target.checked)}
            />
            <span className="toggle-label">
              {useRealValues ? '📏 Real Values' : '🌍 × Earth'}
            </span>
          </label>
        </div>

        <FilterPanel
          filters={filters}
          onFilterChange={handleFilterChange}
          useRealValues={useRealValues}
        />

        <div className="results-header">
          <span>
            Showing {planets.length} of {total} exoplanets
          </span>
        </div>

        <ExoplanetList
          planets={planets}
          loading={loading}
          error={error}
          onSelectPlanet={handleSelectPlanet}
          useRealValues={useRealValues}
        />

        {totalPages > 1 && (
          <div className="pagination">
            <button
              onClick={() => handlePageChange(-1)}
              disabled={currentPage <= 1}
              className="btn btn-secondary"
            >
              ← Previous
            </button>
            <span className="pagination-info">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => handlePageChange(1)}
              disabled={currentPage >= totalPages}
              className="btn btn-secondary"
            >
              Next →
            </button>
          </div>
        )}
      </main>

      {selectedPlanet && (
        <ExoplanetDetail planet={selectedPlanet} onClose={handleCloseDetail} useRealValues={useRealValues} />
      )}
    </div>
  );
}
