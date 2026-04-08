import { useMemo } from 'react';

interface PlanetVisualProps {
  radiusEarth: number | null | undefined;
  temperatureK: number | null | undefined;
  insolationFlux: number | null | undefined;
  name?: string;
  size?: number; // px diameter, default 120
  showLabel?: boolean;
  className?: string;
}

/**
 * Map equilibrium temperature to a surface color palette.
 * Based on blackbody-like color progression + planetary science intuition.
 */
function temperatureColors(tempK: number | null | undefined): {
  core: string;
  surface: string;
  highlight: string;
  band1?: string;
  band2?: string;
} {
  if (tempK == null || tempK <= 0) {
    // Unknown — neutral grey-blue
    return { core: '#4a5568', surface: '#718096', highlight: '#a0aec0' };
  }
  if (tempK < 80) {
    // Deep freeze — methane ice (Neptune-like)
    return { core: '#1a365d', surface: '#2b6cb0', highlight: '#63b3ed', band1: '#1e3a5f', band2: '#2c5282' };
  }
  if (tempK < 150) {
    // Ice world — cyan/blue-white
    return { core: '#1a4731', surface: '#38b2ac', highlight: '#81e6d9', band1: '#234e52', band2: '#285e61' };
  }
  if (tempK < 200) {
    // Frozen — teal/blue-green
    return { core: '#1c4532', surface: '#48bb78', highlight: '#9ae6b4', band1: '#22543d', band2: '#276749' };
  }
  if (tempK < 250) {
    // Cold but nearing habitable — greenish
    return { core: '#22543d', surface: '#68d391', highlight: '#c6f6d5', band1: '#276749', band2: '#48bb78' };
  }
  if (tempK < 273) {
    // Just below freezing — Earth-like cool
    return { core: '#2a4365', surface: '#4299e1', highlight: '#bee3f8', band1: '#2b6cb0', band2: '#3182ce' };
  }
  if (tempK < 300) {
    // Temperate — Earth-like green/brown
    return { core: '#22543d', surface: '#48bb78', highlight: '#f6e05e', band1: '#744210', band2: '#553c9a' };
  }
  if (tempK < 350) {
    // Warm — yellowish/tropical
    return { core: '#744210', surface: '#d69e2e', highlight: '#faf089', band1: '#975a16', band2: '#dd6b20' };
  }
  if (tempK < 500) {
    // Hot — orange
    return { core: '#7b341e', surface: '#dd6b20', highlight: '#fbd38d', band1: '#9b2c2c', band2: '#c05621' };
  }
  if (tempK < 800) {
    // Very hot — red-orange
    return { core: '#742a2a', surface: '#e53e3e', highlight: '#fc8181', band1: '#9b2c2c', band2: '#c53030' };
  }
  if (tempK < 1500) {
    // Lava world — deep red with orange glow
    return { core: '#4a1c1c', surface: '#c53030', highlight: '#f6ad55', band1: '#742a2a', band2: '#9b2c2c' };
  }
  // Extreme — white hot
  return { core: '#4a4a4a', surface: '#e2e8f0', highlight: '#ffffff', band1: '#718096', band2: '#a0aec0' };
}

/**
 * Determine planet "type" for visual styling.
 */
function planetType(
  radiusEarth: number | null | undefined,
): 'rocky' | 'mini-neptune' | 'gas-giant' | 'unknown' {
  if (radiusEarth == null || radiusEarth <= 0) return 'unknown';
  if (radiusEarth < 1.5) return 'rocky';
  if (radiusEarth < 4.0) return 'mini-neptune';
  return 'gas-giant';
}

/**
 * A pure-CSS procedural planet sphere, styled from physical parameters.
 * No WebGL — just radial gradients and pseudo-element atmosphere glow.
 */
export default function PlanetVisual({
  radiusEarth,
  temperatureK,
  insolationFlux,
  name,
  size = 120,
  showLabel = true,
  className = '',
}: PlanetVisualProps) {
  const colors = useMemo(() => temperatureColors(temperatureK), [temperatureK]);
  const type = useMemo(() => planetType(radiusEarth), [radiusEarth]);

  // Atmosphere glow intensity based on insolation flux
  const glowIntensity = useMemo(() => {
    if (insolationFlux == null || insolationFlux <= 0) return 0.3;
    // Clamp to 0.3–1.0 range
    return Math.min(1, Math.max(0.3, insolationFlux / 2.0));
  }, [insolationFlux]);

  // Build the CSS radial gradient for the sphere surface
  const sphereGradient = useMemo(() => {
    if (type === 'gas-giant') {
      // Gas giants get banded appearance via multiple color stops
      return `radial-gradient(circle at 35% 35%, ${colors.highlight}, ${colors.surface} 40%, ${colors.band1 || colors.core} 60%, ${colors.band2 || colors.core} 80%, ${colors.core})`;
    }
    if (type === 'mini-neptune') {
      // Mini-Neptunes: softer gradient with hint of bands
      return `radial-gradient(circle at 35% 35%, ${colors.highlight}, ${colors.surface} 50%, ${colors.core} 85%, ${colors.band1 || colors.core})`;
    }
    // Rocky: sharp gradient with surface detail
    return `radial-gradient(circle at 35% 35%, ${colors.highlight}, ${colors.surface} 45%, ${colors.core} 90%, #1a202c)`;
  }, [colors, type]);

  // Shadow color matches the planet's surface color
  const shadowColor = colors.surface;

  return (
    <div className={`planet-visual ${className}`} style={{ width: size, textAlign: 'center' }}>
      <div
        className="planet-sphere"
        style={{
          width: size,
          height: size,
          background: sphereGradient,
          boxShadow: `
            inset -${size / 6}px -${size / 8}px ${size / 4}px rgba(0,0,0,0.5),
            0 0 ${size / 3}px ${shadowColor}${Math.round(glowIntensity * 40).toString(16).padStart(2, '0')},
            0 0 ${size / 1.5}px ${shadowColor}${Math.round(glowIntensity * 15).toString(16).padStart(2, '0')}
          `,
          '--atmosphere-opacity': glowIntensity,
        } as React.CSSProperties}
      >
        {/* Atmosphere halo */}
        <div
          className="planet-atmosphere"
          style={{
            boxShadow: `0 0 ${size / 4}px ${size / 8}px ${colors.highlight}${Math.round(glowIntensity * 60).toString(16).padStart(2, '0')}`,
          }}
        />
      </div>
      {showLabel && name && (
        <div className="planet-visual-label">{name}</div>
      )}
      {showLabel && radiusEarth != null && radiusEarth > 0 && (
        <div className="planet-visual-size">{radiusEarth.toFixed(2)}× Earth</div>
      )}
    </div>
  );
}
