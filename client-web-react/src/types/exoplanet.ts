export interface Exoplanet {
  id: number;
  name: string;
  hostname: string | null;
  discovery_year: number | null;
  discovery_method: string | null;
  radius_earth: number | null;
  mass_earth: number | null;
  orbital_period_days: number | null;
  equilibrium_temperature_k: number | null;
  distance_light_years: number | null;
  semi_major_axis_au: number | null;
  insolation_flux: number | null;
  constellation: string;
  habitable_zone: boolean;
}

export interface ExoplanetListResponse {
  items: Exoplanet[];
  total: number;
  page: number;
  page_size: number;
}

export interface ExoplanetStats {
  total_count: number;
  habitable_zone_count: number;
  average_radius_earth: number | null;
  closest_planet_name: string | null;
  closest_planet_distance_ly: number | null;
  detection_methods: Record<string, number>;
}

export interface CalculateRequest {
  planet_id: number;
  user_weight_kg: number;
}

export interface CalculateResponse {
  planet_name: string;
  user_weight_kg: number;
  weight_on_planet_kg: number | null;
  surface_gravity_m_s2: number | null;
  gravity_ratio_to_earth: number | null;
  travel_time_walking: string | null;
  travel_time_car: string | null;
  travel_time_plane: string | null;
  travel_time_voyager: string | null;
  travel_time_light: string | null;
  temperature_verdict: string | null;
  gravity_verdict: string | null;
}

export interface ExoplanetFilters {
  search?: string;
  min_radius?: number;
  max_radius?: number;
  min_mass?: number;
  max_mass?: number;
  habitable_zone?: boolean;
  constellation?: string;
  page?: number;
  page_size?: number;
}
