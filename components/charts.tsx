"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
  AreaChart,
  Area,
  LineChart,
  Line,
} from "recharts";
import { formatNumber } from "@/lib/utils";

interface ChartData {
  name: string;
  value: number;
  color?: string;
}

const ZONE_COLORS = {
  "Zone III (Rouge)": "#e31a1c",
  "Zone II (Orange)": "#ff7f00",
  "Zone 0/I (Vert)": "#33a02c",
};

const TYPE_COLORS = ["#1B5E20", "#4CAF50", "#8BC34A", "#CDDC39"];

export function ZoneBarChart({ data }: { data: ChartData[] }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
        <XAxis
          dataKey="name"
          tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
          tickLine={{ stroke: "hsl(var(--border))" }}
        />
        <YAxis
          tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
          tickLine={{ stroke: "hsl(var(--border))" }}
          tickFormatter={(value) => `${(value / 1000000).toFixed(0)}M`}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "hsl(var(--card))",
            border: "1px solid hsl(var(--border))",
            borderRadius: "12px",
            boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
          }}
          labelStyle={{ color: "hsl(var(--foreground))", fontWeight: 600 }}
          formatter={(value: number) => [formatNumber(value) + " DZD", "Capital"]}
        />
        <Bar dataKey="value" radius={[8, 8, 0, 0]}>
          {data.map((entry, index) => (
            <Cell
              key={`cell-${index}`}
              fill={ZONE_COLORS[entry.name as keyof typeof ZONE_COLORS] || TYPE_COLORS[index % TYPE_COLORS.length]}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

export function ZonePieChart({ data }: { data: ChartData[] }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={100}
          paddingAngle={2}
          dataKey="value"
          nameKey="name"
          label={({ name, percent }) => `${(percent * 100).toFixed(0)}%`}
          labelLine={false}
        >
          {data.map((entry, index) => (
            <Cell
              key={`cell-${index}`}
              fill={ZONE_COLORS[entry.name as keyof typeof ZONE_COLORS] || TYPE_COLORS[index % TYPE_COLORS.length]}
            />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            backgroundColor: "hsl(var(--card))",
            border: "1px solid hsl(var(--border))",
            borderRadius: "12px",
          }}
          formatter={(value: number) => [formatNumber(value) + " DZD", "Capital"]}
        />
        <Legend
          wrapperStyle={{ fontSize: "12px" }}
          formatter={(value) => <span style={{ color: "hsl(var(--foreground))" }}>{value}</span>}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}

export function TypeBarChart({ data }: { data: ChartData[] }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} layout="vertical" margin={{ top: 20, right: 30, left: 100, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
        <XAxis
          type="number"
          tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
          tickFormatter={(value) => `${(value / 1000000).toFixed(0)}M`}
        />
        <YAxis
          dataKey="name"
          type="category"
          tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
          width={90}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "hsl(var(--card))",
            border: "1px solid hsl(var(--border))",
            borderRadius: "12px",
          }}
          formatter={(value: number) => [formatNumber(value) + " DZD", "Capital"]}
        />
        <Bar dataKey="value" radius={[0, 8, 8, 0]} fill="#1B5E20">
          {data.map((_, index) => (
            <Cell key={`cell-${index}`} fill={TYPE_COLORS[index % TYPE_COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

export function HistogramChart({ data, var995 }: { data: number[]; var995: number }) {
  // Create histogram bins
  const positiveLosses = data.filter((d) => d > 0);
  if (positiveLosses.length === 0) return null;

  const max = Math.max(...positiveLosses);
  const binCount = 30;
  const binWidth = max / binCount;
  const bins: { range: string; count: number; midpoint: number }[] = [];

  for (let i = 0; i < binCount; i++) {
    const start = i * binWidth;
    const end = (i + 1) * binWidth;
    const count = positiveLosses.filter((v) => v >= start && v < end).length;
    bins.push({
      range: `${(start / 1000000).toFixed(1)}M`,
      count,
      midpoint: (start + end) / 2,
    });
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={bins} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <defs>
          <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#1B5E20" stopOpacity={0.8} />
            <stop offset="95%" stopColor="#1B5E20" stopOpacity={0.1} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
        <XAxis
          dataKey="range"
          tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 10 }}
          interval={4}
        />
        <YAxis tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }} />
        <Tooltip
          contentStyle={{
            backgroundColor: "hsl(var(--card))",
            border: "1px solid hsl(var(--border))",
            borderRadius: "12px",
          }}
          formatter={(value: number) => [value, "Occurrences"]}
        />
        <Area
          type="monotone"
          dataKey="count"
          stroke="#1B5E20"
          fillOpacity={1}
          fill="url(#colorCount)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export function RiskGauge({ score }: { score: number }) {
  const getColor = () => {
    if (score < 40) return "#33a02c";
    if (score < 75) return "#ff7f00";
    return "#e31a1c";
  };

  const circumference = 2 * Math.PI * 80;
  const strokeDashoffset = circumference - (score / 100) * circumference * 0.75;

  return (
    <div className="flex flex-col items-center justify-center">
      <svg width="200" height="150" viewBox="0 0 200 150">
        {/* Background arc */}
        <path
          d="M 20 130 A 80 80 0 0 1 180 130"
          fill="none"
          stroke="hsl(var(--muted))"
          strokeWidth="16"
          strokeLinecap="round"
        />
        {/* Colored segments */}
        <path
          d="M 20 130 A 80 80 0 0 1 65 45"
          fill="none"
          stroke="#33a02c"
          strokeWidth="16"
          strokeLinecap="round"
          opacity="0.3"
        />
        <path
          d="M 65 45 A 80 80 0 0 1 135 45"
          fill="none"
          stroke="#ff7f00"
          strokeWidth="16"
          strokeLinecap="round"
          opacity="0.3"
        />
        <path
          d="M 135 45 A 80 80 0 0 1 180 130"
          fill="none"
          stroke="#e31a1c"
          strokeWidth="16"
          strokeLinecap="round"
          opacity="0.3"
        />
        {/* Value indicator */}
        <circle
          cx="100"
          cy="130"
          r="80"
          fill="none"
          stroke={getColor()}
          strokeWidth="16"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          transform="rotate(135 100 130)"
          style={{ transition: "stroke-dashoffset 1s ease-out" }}
        />
        {/* Center text */}
        <text
          x="100"
          y="115"
          textAnchor="middle"
          className="text-3xl font-bold"
          fill="hsl(var(--foreground))"
        >
          {score.toFixed(0)}%
        </text>
        <text
          x="100"
          y="135"
          textAnchor="middle"
          className="text-sm"
          fill="hsl(var(--muted-foreground))"
        >
          Score de risque
        </text>
      </svg>
    </div>
  );
}
