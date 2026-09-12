const CITIES: Array<[number, number, string]> = [
  [72, 10, "Cairo"],
  [5, 33, "Dakar"],
  [30, 46.5, "Lagos"],
  [81, 41, "Addis Ababa"],
  [75, 56, "Nairobi"],
  [55, 91, "Johannesburg"],
];

/**
 * A dot-matrix silhouette of Africa: a grid of ink dots clipped to the
 * continent's outline, with pulsing accent markers on major capitals.
 * Pure SVG (SMIL animation) — renders on the server, no JS required.
 */
export default function AfricaDotMap({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 100 112" className={className} aria-hidden="true" focusable="false">
      <defs>
        <pattern id="africa-dots" width="2.6" height="2.6" patternUnits="userSpaceOnUse">
          <circle cx="1.3" cy="1.3" r="0.6" className="fill-ink/25" />
        </pattern>
        <clipPath id="africa-shape">
          {/* mainland */}
          <path d="M 20 10 L 33 5 L 46 2 L 57 5 L 70 7 L 77 13 L 79 24 L 84 32 L 96 39 L 88 46 L 79 55 L 73 64 L 68 76 L 64 86 L 56 100 L 47 104 L 41 96 L 38 84 L 36 70 L 34 58 L 37 52 L 30 48 L 20 49 L 12 45 L 4 38 L 2 33 L 6 24 L 13 15 Z" />
          {/* Madagascar */}
          <path d="M 84 72 L 88 68 L 90 74 L 86 88 L 81 84 L 83 76 Z" />
        </clipPath>
      </defs>

      <g clipPath="url(#africa-shape)">
        <rect width="100" height="112" fill="url(#africa-dots)" />
      </g>

      {CITIES.map(([x, y, name], i) => (
        <g key={name}>
          <circle cx={x} cy={y} r="1" className="fill-accent" />
          <circle cx={x} cy={y} r="1" className="stroke-accent" fill="none" strokeWidth="0.4">
            <animate attributeName="r" values="1;4.5" dur="3s" begin={`${i * 0.5}s`} repeatCount="indefinite" />
            <animate attributeName="opacity" values="0.8;0" dur="3s" begin={`${i * 0.5}s`} repeatCount="indefinite" />
          </circle>
        </g>
      ))}
    </svg>
  );
}
