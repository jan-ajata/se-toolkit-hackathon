import { useState, useEffect, useCallback } from 'react';
import type { Exoplanet, ExoplanetFilters, ExoplanetStats } from './types/exoplanet';
import { getExoplanets, getExoplanetStats, getExoplanet } from './api/client';
import StatsCards from './components/StatsCards';
import FilterPanel from './components/FilterPanel';
import ExoplanetList from './components/ExoplanetList';
import ExoplanetDetail from './components/ExoplanetDetail';
import PlanetOfDay from './components/PlanetOfDay';
import ComparisonModal from './components/ComparisonModal';
import './App.css';

export default function App() {
  const [planets, setPlanets] = useState<Exoplanet[]>([]);
  const [total, setTotal] = useState(0);
  const [stats, setStats] = useState<ExoplanetStats | null>(null);
  const [selectedPlanet, setSelectedPlanet] = useState<Exoplanet | null>(null);
  const [useRealValues, setUseRealValues] = useState(false);

  // V2: Comparison state
  const [compareMode, setCompareMode] = useState(false);
  const [comparePlanets, setComparePlanets] = useState<Exoplanet[]>([]);
  const [showComparison, setShowComparison] = useState(false);

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

  // V2: Comparison handlers
  const handleToggleCompareMode = useCallback(() => {
    setCompareMode((prev) => !prev);
    setComparePlanets([]);
    setShowComparison(false);
  }, []);

  const handleSelectForCompare = useCallback((planet: Exoplanet) => {
    setComparePlanets((prev) => {
      if (prev.length >= 2) return prev;
      if (prev.find((p) => p.id === planet.id)) return prev;
      return [...prev, planet];
    });
  }, []);

  const handleLaunchComparison = useCallback(() => {
    if (comparePlanets.length !== 2) return;
    setShowComparison(true);
  }, [comparePlanets]);

  const handleCloseComparison = useCallback(() => {
    setShowComparison(false);
    setComparePlanets([]);
    setCompareMode(false);
  }, []);

  const handleExplorePlanetOfDay = useCallback(async (planetId: number) => {
    try {
      const planet = await getExoplanet(planetId);
      setSelectedPlanet(planet);
    } catch (err) {
      // Silently fail - user can still find the planet manually
    }
  }, []);

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
        {/* V2: Planet of the Day */}
        <PlanetOfDay onExplorePlanet={handleExplorePlanetOfDay} />

        <div className="toolbar">
          <StatsCards stats={stats} loading={statsLoading} error={statsError} />
          <div className="toolbar-actions">
            <button
              onClick={handleToggleCompareMode}
              className={`btn ${compareMode ? 'btn-primary' : 'btn-secondary'}`}
            >
              {compareMode ? '✖ Cancel Compare' : '🔬 Compare Planets'}
            </button>
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
        </div>

        {/* V2: Compare mode banner */}
        {compareMode && (
          <div className="compare-mode-banner">
            <span>
              Select 2 planets to compare ({comparePlanets.length}/2 selected)
            </span>
            {comparePlanets.length === 2 && (
              <button onClick={handleLaunchComparison} className="btn btn-primary">
                📊 Compare Now
              </button>
            )}
            {comparePlanets.length > 0 && (
              <div className="selected-for-compare">
                {comparePlanets.map((p) => (
                  <span key={p.id} className="selected-planet-tag">
                    {p.name}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}

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
          onSelectPlanet={compareMode ? handleSelectForCompare : handleSelectPlanet}
          useRealValues={useRealValues}
          compareMode={compareMode}
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

      {!compareMode && selectedPlanet && (
        <ExoplanetDetail planet={selectedPlanet} onClose={handleCloseDetail} useRealValues={useRealValues} />
      )}

      {/* V2: Comparison Modal */}
      {showComparison && comparePlanets.length === 2 && (
        <ComparisonModal
          planetA={comparePlanets[0]}
          planetB={comparePlanets[1]}
          onClose={handleCloseComparison}
        />
      )}
    </div>
  );
}
