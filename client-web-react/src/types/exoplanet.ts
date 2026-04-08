export interface Exoplanet {
  id: number;
  name: string;
  hostname: string;
  discovery_year: number;
  discovery_method: string;
  radius_earth: number;
  mass_earth: number | null;
  mass_estimated: boolean;
  orbital_period_days: number;
  equilibrium_temperature_k: number | null;
  distance_light_years: number | null;
  semi_major_axis_au: number | null;
  insolation_flux: number | null;
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
  average_radius_earth: number;
  closest_planet_name: string;
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
  surface_gravity_ms2: number | null;
  escape_velocity_kms: number | null;
  travel_time_walking: string;
  travel_time_car: string;
  travel_time_plane: string;
  travel_time_voyager: string;
  travel_time_light: string;
  radio_signal_time_to_earth: string;
  temperature_verdict: string;
  gravity_verdict: string;
}

export interface CompareRequest {
  planet_a_id: number;
  planet_b_id: number;
}

export interface CompareResponse {
  planet_a: Exoplanet;
  planet_b: Exoplanet;
  earth_reference: Record<string, number>;
}

export interface PlanetOfDayResponse {
  planet: Exoplanet;
  fun_fact: string;
}

export interface ExoplanetFilters {
  search?: string;
  min_radius?: number;
  max_radius?: number;
  min_mass?: number;
  max_mass?: number;
  habitable_zone?: boolean;
  page?: number;
  page_size?: number;
}
