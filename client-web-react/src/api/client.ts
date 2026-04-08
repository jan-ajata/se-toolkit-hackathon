import type {
  Exoplanet,
  ExoplanetListResponse,
  ExoplanetStats,
  CalculateRequest,
  CalculateResponse,
  CompareRequest,
  PlanetOfDayResponse,
  ExoplanetFilters,
} from '../types/exoplanet';

const API_BASE = import.meta.env.VITE_API_BASE || '';
const API_KEY = import.meta.env.VITE_API_KEY || 'dev-api-key';

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY,
      ...init?.headers,
    },
    ...init,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export async function getExoplanets(filters: ExoplanetFilters = {}): Promise<ExoplanetListResponse> {
  const params = new URLSearchParams();

  if (filters.search) params.set('search', filters.search);
  if (filters.min_radius != null) params.set('min_radius', String(filters.min_radius));
  if (filters.max_radius != null) params.set('max_radius', String(filters.max_radius));
  if (filters.min_mass != null) params.set('min_mass', String(filters.min_mass));
  if (filters.max_mass != null) params.set('max_mass', String(filters.max_mass));
  if (filters.habitable_zone != null) params.set('habitable_zone', String(filters.habitable_zone));
  if (filters.page != null) params.set('page', String(filters.page));
  if (filters.page_size != null) params.set('page_size', String(filters.page_size));

  const queryString = params.toString();
  return fetchJson<ExoplanetListResponse>(`/exoplanets/${queryString ? `?${queryString}` : ''}`);
}

export async function getExoplanet(id: number): Promise<Exoplanet> {
  return fetchJson<Exoplanet>(`/exoplanets/${id}`);
}

export async function getExoplanetStats(): Promise<ExoplanetStats> {
  return fetchJson<ExoplanetStats>('/exoplanets/stats');
}

export async function calculateSurvival(payload: CalculateRequest): Promise<CalculateResponse> {
  return fetchJson<CalculateResponse>('/exoplanets/calculate', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function comparePlanets(payload: CompareRequest): Promise<{ planet_a: Exoplanet; planet_b: Exoplanet; earth_reference: Record<string, number> }> {
  return fetchJson<{ planet_a: Exoplanet; planet_b: Exoplanet; earth_reference: Record<string, number> }>('/exoplanets/compare', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function getPlanetOfDay(): Promise<PlanetOfDayResponse> {
  return fetchJson<PlanetOfDayResponse>('/exoplanets/planet-of-the-day');
}
