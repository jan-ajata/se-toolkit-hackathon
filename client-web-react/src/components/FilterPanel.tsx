import { useState, useCallback, useMemo } from 'react';
import type { ExoplanetFilters } from '../types/exoplanet';

// Physical constants
const EARTH_RADIUS_KM = 6371;
const EARTH_MASS_KG = 5.972e24;

interface FilterPanelProps {
  filters: ExoplanetFilters;
  onFilterChange: (filters: ExoplanetFilters) => void;
  useRealValues: boolean;
}

/** Convert Earth-relative → real for display */
function toReal(earthValue: number | undefined, unit: 'radius' | 'mass'): number | undefined {
  if (earthValue == null) return undefined;
  return unit === 'radius' ? earthValue * EARTH_RADIUS_KM : earthValue * EARTH_MASS_KG;
}

/** Convert real → Earth-relative for API */
function toEarth(realValue: number | undefined, unit: 'radius' | 'mass'): number | undefined {
  if (realValue == null) return undefined;
  return unit === 'radius' ? realValue / EARTH_RADIUS_KM : realValue / EARTH_MASS_KG;
}

export default function FilterPanel({ filters, onFilterChange, useRealValues }: FilterPanelProps) {
  const [search, setSearch] = useState(filters.search ?? '');

  /* ---- display values (converted from stored Earth-relative) ---- */
  const displayMinRadius = useMemo(
    () => toReal(filters.min_radius, 'radius'),
    [filters.min_radius]
  );
  const displayMaxRadius = useMemo(
    () => toReal(filters.max_radius, 'radius'),
    [filters.max_radius]
  );
  const displayMinMass = useMemo(
    () => toReal(filters.min_mass, 'mass'),
    [filters.min_mass]
  );
  const displayMaxMass = useMemo(
    () => toReal(filters.max_mass, 'mass'),
    [filters.max_mass]
  );

  /* ---- handlers ---- */
  const handleSearchSubmit = useCallback(() => {
    onFilterChange({ ...filters, search: search || undefined, page: 1 });
  }, [search, filters, onFilterChange]);

  const handleRadiusChange = useCallback(
    (which: 'min' | 'max', raw: string) => {
      const num = raw === '' ? undefined : parseFloat(raw);
      const earthVal = toEarth(num, 'radius');
      const key = which === 'min' ? 'min_radius' : 'max_radius';
      onFilterChange({ ...filters, [key]: earthVal, page: 1 });
    },
    [filters, onFilterChange]
  );

  const handleMassChange = useCallback(
    (which: 'min' | 'max', raw: string) => {
      const num = raw === '' ? undefined : parseFloat(raw);
      const earthVal = toEarth(num, 'mass');
      const key = which === 'min' ? 'min_mass' : 'max_mass';
      onFilterChange({ ...filters, [key]: earthVal, page: 1 });
    },
    [filters, onFilterChange]
  );

  const handleCheckboxChange = useCallback(
    (checked: boolean) => {
      onFilterChange({ ...filters, habitable_zone: checked || undefined, page: 1 });
    },
    [filters, onFilterChange]
  );

  const handleReset = useCallback(() => {
    setSearch('');
    onFilterChange({ page: 1, page_size: filters.page_size });
  }, [onFilterChange, filters.page_size]);

  /* ---- units ---- */
  const radiusUnit = useRealValues ? 'km' : '×Earth';
  const massUnit = useRealValues ? 'kg' : '×Earth';

  return (
    <div className="filter-panel">
      <h3>🔍 Filters</h3>

      {/* Search bar — full width, separate row */}
      <div className="filter-search-row">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearchSubmit()}
          placeholder="Search by planet name, e.g. Kepler-442b"
          className="search-input"
        />
        <button onClick={handleSearchSubmit} className="btn btn-primary">
          Search
        </button>
        <button onClick={handleReset} className="btn btn-secondary">
          Reset
        </button>
      </div>

      <div className="filter-grid">
        {/* Radius range — grouped */}
        <div className="filter-range-group">
          <span className="filter-range-label">Radius ({radiusUnit})</span>
          <div className="filter-range-inputs">
            <input
              type="number"
              min="0"
              step={useRealValues ? 100 : 0.1}
              value={displayMinRadius ?? ''}
              onChange={(e) => handleRadiusChange('min', e.target.value)}
              placeholder={`Min ${radiusUnit}`}
              className="range-min"
            />
            <span className="range-separator">–</span>
            <input
              type="number"
              min="0"
              step={useRealValues ? 100 : 0.1}
              value={displayMaxRadius ?? ''}
              onChange={(e) => handleRadiusChange('max', e.target.value)}
              placeholder={`Max ${radiusUnit}`}
              className="range-max"
            />
          </div>
        </div>

        {/* Mass range — grouped */}
        <div className="filter-range-group">
          <span className="filter-range-label">Mass ({massUnit})</span>
          <div className="filter-range-inputs">
            <input
              type="number"
              min="0"
              step={useRealValues ? 1e23 : 0.1}
              value={displayMinMass ?? ''}
              onChange={(e) => handleMassChange('min', e.target.value)}
              placeholder={`Min ${massUnit}`}
              className="range-min"
            />
            <span className="range-separator">–</span>
            <input
              type="number"
              min="0"
              step={useRealValues ? 1e23 : 0.1}
              value={displayMaxMass ?? ''}
              onChange={(e) => handleMassChange('max', e.target.value)}
              placeholder={`Max ${massUnit}`}
              className="range-max"
            />
          </div>
        </div>

        {/* Habitable zone */}
        <div className="filter-group filter-checkbox">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={filters.habitable_zone ?? false}
              onChange={(e) => handleCheckboxChange(e.target.checked)}
            />
            Habitable Zone Only
          </label>
        </div>
      </div>
    </div>
  );
}
