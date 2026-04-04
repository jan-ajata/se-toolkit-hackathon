import { useState, useCallback } from 'react';
import type { ExoplanetFilters } from '../types/exoplanet';

interface FilterPanelProps {
  filters: ExoplanetFilters;
  onFilterChange: (filters: ExoplanetFilters) => void;
  constellations: string[];
}

export default function FilterPanel({ filters, onFilterChange, constellations }: FilterPanelProps) {
  const [search, setSearch] = useState(filters.search ?? '');

  const handleSearchSubmit = useCallback(() => {
    onFilterChange({ ...filters, search: search || undefined, page: 1 });
  }, [search, filters, onFilterChange]);

  const handleNumberChange = useCallback(
    (key: keyof ExoplanetFilters, value: string) => {
      const numValue = value === '' ? undefined : parseFloat(value);
      onFilterChange({ ...filters, [key]: numValue, page: 1 });
    },
    [filters, onFilterChange]
  );

  const handleCheckboxChange = useCallback(
    (checked: boolean) => {
      onFilterChange({ ...filters, habitable_zone: checked || undefined, page: 1 });
    },
    [filters, onFilterChange]
  );

  const handleConstellationChange = useCallback(
    (e: React.ChangeEvent<HTMLSelectElement>) => {
      const value = e.target.value || undefined;
      onFilterChange({ ...filters, constellation: value, page: 1 });
    },
    [filters, onFilterChange]
  );

  const handleReset = useCallback(() => {
    setSearch('');
    onFilterChange({ page: 1, page_size: filters.page_size });
  }, [onFilterChange, filters.page_size]);

  return (
    <div className="filter-panel">
      <h3>🔍 Filters</h3>
      <div className="filter-grid">
        <div className="filter-group">
          <label>Search by name</label>
          <div className="search-input-group">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearchSubmit()}
              placeholder="e.g. Kepler-442b"
            />
            <button onClick={handleSearchSubmit} className="btn btn-primary">
              Search
            </button>
          </div>
        </div>

        <div className="filter-group">
          <label>Min Radius (×Earth)</label>
          <input
            type="number"
            min="0"
            step="0.1"
            value={filters.min_radius ?? ''}
            onChange={(e) => handleNumberChange('min_radius', e.target.value)}
            placeholder="Any"
          />
        </div>

        <div className="filter-group">
          <label>Max Radius (×Earth)</label>
          <input
            type="number"
            min="0"
            step="0.1"
            value={filters.max_radius ?? ''}
            onChange={(e) => handleNumberChange('max_radius', e.target.value)}
            placeholder="Any"
          />
        </div>

        <div className="filter-group">
          <label>Min Mass (×Earth)</label>
          <input
            type="number"
            min="0"
            step="0.1"
            value={filters.min_mass ?? ''}
            onChange={(e) => handleNumberChange('min_mass', e.target.value)}
            placeholder="Any"
          />
        </div>

        <div className="filter-group">
          <label>Max Mass (×Earth)</label>
          <input
            type="number"
            min="0"
            step="0.1"
            value={filters.max_mass ?? ''}
            onChange={(e) => handleNumberChange('max_mass', e.target.value)}
            placeholder="Any"
          />
        </div>

        <div className="filter-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={filters.habitable_zone ?? false}
              onChange={(e) => handleCheckboxChange(e.target.checked)}
            />
            Habitable Zone Only
          </label>
        </div>

        <div className="filter-group">
          <label>Constellation</label>
          <select value={filters.constellation ?? ''} onChange={handleConstellationChange}>
            <option value="">All Constellations</option>
            {constellations.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <button onClick={handleReset} className="btn btn-secondary">
            Reset Filters
          </button>
        </div>
      </div>
    </div>
  );
}
