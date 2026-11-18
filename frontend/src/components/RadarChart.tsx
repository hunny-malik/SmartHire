import React from 'react';

interface RadarDataPoint {
  label: string;
  value: number; // 0 to 100
  maxValue?: number;
}

interface RadarChartProps {
  data: RadarDataPoint[];
  size?: number;
  color?: string;
  fillColor?: string;
}

export const RadarChart: React.FC<RadarChartProps> = ({
  data,
  size = 280,
  color = '#6366f1',
  fillColor = 'rgba(99, 102, 241, 0.25)',
}) => {
  if (!data || data.length < 3) return null;

  const center = size / 2;
  const radius = (size / 2) - 45;
  const numPoints = data.length;
  const angleStep = (Math.PI * 2) / numPoints;

  // Concentric polygon levels (25%, 50%, 75%, 100%)
  const levels = [0.25, 0.5, 0.75, 1.0];

  // Helper to get coordinates
  const getCoordinates = (index: number, val: number, max: number = 100) => {
    const angle = index * angleStep - Math.PI / 2;
    const r = (val / max) * radius;
    return {
      x: center + r * Math.cos(angle),
      y: center + r * Math.sin(angle),
    };
  };

  // Generate data polygon points
  const pointsString = data
    .map((d, i) => {
      const { x, y } = getCoordinates(i, d.value, d.maxValue || 100);
      return `${x},${y}`;
    })
    .join(' ');

  return (
    <div className="flex flex-col items-center justify-center">
      <svg width={size} height={size} className="overflow-visible select-none">
        {/* Background Grid Circles / Polygons */}
        {levels.map((lvl, lvlIdx) => (
          <polygon
            key={lvlIdx}
            points={Array.from({ length: numPoints })
              .map((_, i) => {
                const angle = i * angleStep - Math.PI / 2;
                const r = radius * lvl;
                return `${center + r * Math.cos(angle)},${center + r * Math.sin(angle)}`;
              })
              .join(' ')}
            fill="none"
            stroke="#1f2937"
            strokeWidth="1"
            strokeDasharray={lvlIdx < 3 ? '2 2' : 'none'}
          />
        ))}

        {/* Axis Spokes from center to vertex */}
        {data.map((_, i) => {
          const angle = i * angleStep - Math.PI / 2;
          const x2 = center + radius * Math.cos(angle);
          const y2 = center + radius * Math.sin(angle);
          return (
            <line
              key={i}
              x1={center}
              y1={center}
              x2={x2}
              y2={y2}
              stroke="#1f2937"
              strokeWidth="1"
            />
          );
        })}

        {/* Data Filled Polygon */}
        <polygon
          points={pointsString}
          fill={fillColor}
          stroke={color}
          strokeWidth="2.5"
          className="transition-all duration-500 ease-out"
        />

        {/* Data Point Markers */}
        {data.map((d, i) => {
          const { x, y } = getCoordinates(i, d.value, d.maxValue || 100);
          return (
            <circle
              key={i}
              cx={x}
              cy={y}
              r="4"
              fill={color}
              stroke="#0f172a"
              strokeWidth="2"
            />
          );
        })}

        {/* Category Labels */}
        {data.map((d, i) => {
          const angle = i * angleStep - Math.PI / 2;
          const labelDist = radius + 22;
          const lx = center + labelDist * Math.cos(angle);
          const ly = center + labelDist * Math.sin(angle);
          
          let textAnchor: 'middle' | 'start' | 'end' = 'middle';
          if (Math.cos(angle) > 0.3) textAnchor = 'start';
          else if (Math.cos(angle) < -0.3) textAnchor = 'end';

          return (
            <text
              key={i}
              x={lx}
              y={ly}
              textAnchor={textAnchor}
              dominantBaseline="central"
              fontSize="10"
              fontWeight="600"
              fill="#94a3b8"
            >
              {d.label} ({d.value}%)
            </text>
          );
        })}
      </svg>
    </div>
  );
};
