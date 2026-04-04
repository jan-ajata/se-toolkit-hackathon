import type { ExoplanetStats } from '../types/exoplanet';

interface StatsCardsProps {
  stats: ExoplanetStats | null;
  loading: boolean;
  error: string | null;
}

export default function StatsCards({ stats, loading, error }: StatsCardsProps) {
  if (loading) {
    return (
      <div className="stats-grid">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="stat-card stat-card-loading">
            <div className="stat-value skeleton" />
            <div className="stat-label skeleton" />
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return <div className="error-banner">Failed to load stats: {error}</div>;
  }

  if (!stats) return null;

  return (
    <div className="stats-grid">
      <div className="stat-card">
        <div className="stat-value">{stats.total_count}</div>
        <div className="stat-label">🪐 Total Discovered</div>
      </div>
      <div className="stat-card stat-card-habitable">
        <div className="stat-value">{stats.habitable_zone_count}</div>
        <div className="stat-label">🌍 In Habitable Zone</div>
      </div>
      <div className="stat-card">
        <div className="stat-value">
          {stats.closest_planet_name ? (
            <span title={stats.closest_planet_distance_ly ? `${stats.closest_planet_distance_ly} ly` : 'Unknown distance'}>
              {stats.closest_planet_name}
            </span>
          ) : (
            'N/A'
          )}
        </div>
        <div className="stat-label">⭐ Closest to Earth</div>
      </div>
      <div className="stat-card">
        <div className="stat-value">
          {stats.average_radius_earth?.toFixed(2) ?? 'N/A'}
        </div>
        <div className="stat-label">📏 Avg Radius (×Earth)</div>
      </div>
    </div>
  );
}
