import type { Exoplanet } from '../types/exoplanet';
import PlanetVisual from './PlanetVisual';

interface PlanetSizeCompareProps {
  planet: Exoplanet;
  maxSize?: number; // max diameter in px for the larger planet, default 180
  minSize?: number; // min diameter in px for the smaller planet, default 30
}

/**
 * Side-by-side planet visualization with Earth as reference.
 * The larger planet gets the max size; Earth (or the smaller planet) scales proportionally.
 * If the target planet is huge, Earth shrinks to show scale.
 * If the target planet is tiny, it shrinks while Earth stays readable.
 */
export default function PlanetSizeCompare({
  planet,
  maxSize = 180,
  minSize = 30,
}: PlanetSizeCompareProps) {
  const earthRadius = 1.0;
  const targetRadius = planet.radius_earth ?? 0;

  // Calculate relative sizes
  const ratio = targetRadius > 0 ? targetRadius / earthRadius : 1;

  let earthSize: number;
  let planetSize: number;

  if (ratio >= 1) {
    // Target is bigger or equal — it gets maxSize, Earth scales down
    planetSize = maxSize;
    earthSize = Math.max(minSize, maxSize / ratio);
  } else {
    // Target is smaller — Earth gets maxSize, target scales down
    earthSize = maxSize;
    planetSize = Math.max(minSize, maxSize * ratio);
  }

  const showEarth = earthSize >= minSize;
  const showTarget = planetSize >= minSize;

  return (
    <div className="planet-size-compare">
      <h4>Size Comparison with Earth</h4>
      <div className="planet-size-visuals">
        {/* Earth */}
        {showEarth ? (
          <div className="planet-size-item">
            <PlanetVisual
              radiusEarth={1.0}
              temperatureK={288}
              insolationFlux={1.0}
              name="Earth"
              size={earthSize}
              showLabel={true}
            />
          </div>
        ) : (
          <div className="planet-size-item planet-too-small">
            <div className="planet-dot" style={{ width: minSize * 0.3, height: minSize * 0.3 }} />
            <div className="planet-visual-label">Earth</div>
            <div className="planet-visual-size">1.00×</div>
          </div>
        )}

        {/* Target planet */}
        {showTarget ? (
          <div className="planet-size-item">
            <PlanetVisual
              radiusEarth={targetRadius}
              temperatureK={planet.equilibrium_temperature_k}
              insolationFlux={planet.insolation_flux}
              name={planet.name}
              size={planetSize}
              showLabel={true}
            />
          </div>
        ) : (
          <div className="planet-size-item planet-too-small">
            <div className="planet-dot" style={{ width: minSize * 0.3, height: minSize * 0.3 }} />
            <div className="planet-visual-label">{planet.name}</div>
            <div className="planet-visual-size">{targetRadius.toFixed(3)}×</div>
          </div>
        )}
      </div>
      <div className="planet-size-ratio">
        {ratio >= 1
          ? `${planet.name} is ${ratio.toFixed(1)}× larger than Earth`
          : ratio > 0
            ? `${planet.name} is ${(1 / ratio).toFixed(1)}× smaller than Earth`
            : `Radius data unavailable for ${planet.name}`}
      </div>
    </div>
  );
}
