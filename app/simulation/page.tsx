"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { HistogramChart } from "@/components/charts";
import { ALL_WILAYAS, runMonteCarloSimulation } from "@/lib/data";
import { formatNumber } from "@/lib/utils";
import {
  Play,
  BarChart3,
  AlertTriangle,
  TrendingUp,
  DollarSign,
  Activity,
  CheckCircle,
  AlertCircle,
  Loader2,
} from "lucide-react";

// Sample portfolio data per wilaya (in real app, this would come from database)
const WILAYA_PORTFOLIO: Record<string, { policies: number; exposure: number; premiums: number }> = {
  ALGER: { policies: 15420, exposure: 45_000_000_000, premiums: 850_000_000 },
  BOUMERDES: { policies: 8750, exposure: 28_000_000_000, premiums: 520_000_000 },
  BLIDA: { policies: 6230, exposure: 18_500_000_000, premiums: 345_000_000 },
  ORAN: { policies: 9870, exposure: 32_000_000_000, premiums: 480_000_000 },
  CONSTANTINE: { policies: 7650, exposure: 24_000_000_000, premiums: 360_000_000 },
  SETIF: { policies: 5430, exposure: 16_000_000_000, premiums: 240_000_000 },
  DEFAULT: { policies: 2500, exposure: 8_000_000_000, premiums: 120_000_000 },
};

export default function SimulationPage() {
  const [selectedWilaya, setSelectedWilaya] = useState("ALGER");
  const [frequency, setFrequency] = useState(0.05);
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<{
    losses: number[];
    meanLoss: number;
    var995: number;
    maxLoss: number;
  } | null>(null);

  const portfolioData =
    WILAYA_PORTFOLIO[selectedWilaya] || WILAYA_PORTFOLIO.DEFAULT;

  const runSimulation = async () => {
    setIsRunning(true);
    setProgress(0);
    setResults(null);

    // Simulate progress
    const progressInterval = setInterval(() => {
      setProgress((prev) => Math.min(prev + 5, 95));
    }, 100);

    // Run simulation in chunks to avoid blocking UI
    await new Promise((resolve) => setTimeout(resolve, 100));

    const simulationResults = runMonteCarloSimulation(
      portfolioData.exposure * 0.3, // 30% of exposure as modeled PML
      frequency,
      100000
    );

    clearInterval(progressInterval);
    setProgress(100);
    setResults(simulationResults);
    setIsRunning(false);
  };

  const getLossRatioStatus = (ratio: number) => {
    if (ratio < 50)
      return {
        status: "Rentable",
        color: "#33a02c",
        bgColor: "bg-green-500/10",
        icon: CheckCircle,
      };
    if (ratio < 80)
      return {
        status: "Sous tension",
        color: "#ff7f00",
        bgColor: "bg-orange-500/10",
        icon: AlertCircle,
      };
    return {
      status: "Deficitaire",
      color: "#e31a1c",
      bgColor: "bg-red-500/10",
      icon: AlertTriangle,
    };
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-[hsl(var(--foreground))]">
          Simulation Stochastique Monte Carlo
        </h1>
        <p className="text-[hsl(var(--muted-foreground))] mt-1">
          Evaluation probabiliste des pertes maximales selon des scenarios sismiques simules
        </p>
      </div>

      {/* Parameters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-[hsl(var(--primary))]" />
            Parametrage du Scenario
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Wilaya Selection */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-[hsl(var(--foreground))]">
                Cible de la simulation (Wilaya)
              </label>
              <select
                value={selectedWilaya}
                onChange={(e) => setSelectedWilaya(e.target.value)}
                className="w-full rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--primary))] transition-all"
              >
                {ALL_WILAYAS.map((w) => (
                  <option key={w.code} value={w.name}>
                    {w.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Frequency Slider */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-[hsl(var(--foreground))]">
                Frequence annuelle d&apos;occurrence (CATNAT)
              </label>
              <div className="space-y-3">
                <input
                  type="range"
                  min="0"
                  max="0.2"
                  step="0.001"
                  value={frequency}
                  onChange={(e) => setFrequency(Number(e.target.value))}
                  className="w-full h-2 rounded-lg appearance-none cursor-pointer accent-[hsl(var(--primary))]"
                  style={{
                    background: `linear-gradient(to right, hsl(var(--primary)) 0%, hsl(var(--primary)) ${
                      (frequency / 0.2) * 100
                    }%, hsl(var(--muted)) ${(frequency / 0.2) * 100}%, hsl(var(--muted)) 100%)`,
                  }}
                />
                <div className="flex justify-between items-center text-xs text-[hsl(var(--muted-foreground))]">
                  <span>0%</span>
                  <div className="flex items-center gap-2">
                    <input
                      type="number"
                      min="0"
                      max="20"
                      step="0.1"
                      value={(frequency * 100).toFixed(1)}
                      onChange={(e) => {
                        const val = Math.min(Math.max(Number(e.target.value) / 100, 0), 0.2);
                        setFrequency(val);
                      }}
                      className="w-16 text-center rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] px-2 py-1 text-sm font-semibold text-[hsl(var(--primary))] outline-none focus:ring-2 focus:ring-[hsl(var(--primary))]"
                    />
                    <span className="font-semibold text-[hsl(var(--primary))]">%</span>
                  </div>
                  <span>20%</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Portfolio Profile */}
      <Card>
        <CardHeader>
          <CardTitle>Profil du Portefeuille Cible (2024)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="rounded-xl bg-[hsl(var(--primary))]/10 p-4">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-xl bg-[hsl(var(--primary))]/20 flex items-center justify-center">
                  <Activity className="h-5 w-5 text-[hsl(var(--primary))]" />
                </div>
                <div>
                  <p className="text-xs text-[hsl(var(--muted-foreground))]">Polices Actives</p>
                  <p className="text-2xl font-bold text-[hsl(var(--primary))]">
                    {formatNumber(portfolioData.policies)}
                  </p>
                </div>
              </div>
            </div>

            <div className="rounded-xl bg-orange-500/10 p-4">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-xl bg-orange-500/20 flex items-center justify-center">
                  <TrendingUp className="h-5 w-5 text-orange-500" />
                </div>
                <div>
                  <p className="text-xs text-[hsl(var(--muted-foreground))]">Exposition Modelisee (PML)</p>
                  <p className="text-2xl font-bold text-orange-500">
                    {formatNumber(portfolioData.exposure * 0.3)} DZD
                  </p>
                </div>
              </div>
            </div>

            <div className="rounded-xl bg-green-500/10 p-4">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-xl bg-green-500/20 flex items-center justify-center">
                  <DollarSign className="h-5 w-5 text-green-500" />
                </div>
                <div>
                  <p className="text-xs text-[hsl(var(--muted-foreground))]">Volume Primes Nettes</p>
                  <p className="text-2xl font-bold text-green-500">
                    {formatNumber(portfolioData.premiums)} DZD
                  </p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Run Simulation Button */}
      <button
        onClick={runSimulation}
        disabled={isRunning}
        className="w-full rounded-xl bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] py-4 font-semibold hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center justify-center gap-2"
      >
        {isRunning ? (
          <>
            <Loader2 className="h-5 w-5 animate-spin" />
            Generation de 100,000 scenarios sismiques... ({progress}%)
          </>
        ) : (
          <>
            <Play className="h-5 w-5" />
            Lancer la Simulation Monte Carlo
          </>
        )}
      </button>

      {/* Progress Bar */}
      {isRunning && (
        <div className="w-full h-2 bg-[hsl(var(--muted))] rounded-full overflow-hidden">
          <div
            className="h-full bg-[hsl(var(--primary))] transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}

      {/* Results */}
      {results && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-fade-in">
          {/* Solvency Indicators */}
          <Card>
            <CardHeader>
              <CardTitle>Indicateurs de Solvabilite</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Mean Loss */}
              <div className="rounded-xl bg-[hsl(var(--muted))] p-4">
                <p className="text-sm text-[hsl(var(--muted-foreground))]">Charge moyenne annuelle</p>
                <p className="text-2xl font-bold text-[hsl(var(--foreground))]">
                  {formatNumber(results.meanLoss)} DZD
                </p>
              </div>

              {/* VaR 99.5% */}
              <div className="rounded-xl bg-red-500/10 border border-red-500/20 p-4">
                <p className="text-sm text-red-500 font-medium">Value at Risk (VaR 99.5%)</p>
                <p className="text-3xl font-bold text-red-500">
                  {formatNumber(results.var995)} DZD
                </p>
                <p className="text-xs text-[hsl(var(--muted-foreground))] mt-1">
                  Perte maximale attendue avec une probabilite de 1-en-200 ans (Standard Solvabilite II)
                </p>
              </div>

              {/* Loss Ratio */}
              {(() => {
                const lossRatio =
                  portfolioData.premiums > 0
                    ? (results.meanLoss / portfolioData.premiums) * 100
                    : 0;
                const status = getLossRatioStatus(lossRatio);
                const Icon = status.icon;

                return (
                  <div
                    className={`rounded-xl p-4 ${status.bgColor} border-l-4`}
                    style={{ borderLeftColor: status.color }}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-[hsl(var(--muted-foreground))]">S/P Technique</p>
                        <p className="text-3xl font-bold" style={{ color: status.color }}>
                          {lossRatio.toFixed(2)}%
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Icon className="h-6 w-6" style={{ color: status.color }} />
                        <span className="font-semibold" style={{ color: status.color }}>
                          {status.status}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })()}

              {/* Additional Stats */}
              <div className="grid grid-cols-2 gap-4">
                <div className="rounded-xl bg-[hsl(var(--muted))] p-4">
                  <p className="text-xs text-[hsl(var(--muted-foreground))]">Scenarios simules</p>
                  <p className="text-lg font-semibold text-[hsl(var(--foreground))]">100,000</p>
                </div>
                <div className="rounded-xl bg-[hsl(var(--muted))] p-4">
                  <p className="text-xs text-[hsl(var(--muted-foreground))]">Perte maximale</p>
                  <p className="text-lg font-semibold text-[hsl(var(--foreground))]">
                    {formatNumber(results.maxLoss)} DZD
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Distribution Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Distribution des Pertes Modelisees</CardTitle>
            </CardHeader>
            <CardContent>
              <HistogramChart data={results.losses} var995={results.var995} />
              <div className="mt-4 flex items-center justify-center gap-6 text-sm">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-[hsl(var(--primary))]" />
                  <span className="text-[hsl(var(--muted-foreground))]">Frequence des pertes</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Info Box */}
      <Card className="border-l-4 border-l-[hsl(var(--accent))]">
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-[hsl(var(--accent))] mt-0.5" />
            <div>
              <h4 className="font-semibold text-[hsl(var(--foreground))]">
                A propos de la simulation Monte Carlo
              </h4>
              <p className="text-sm text-[hsl(var(--muted-foreground))] mt-1">
                Cette simulation utilise 100,000 scenarios aleatoires pour estimer la distribution
                des pertes potentielles. Le modele prend en compte la frequence des evenements
                (distribution de Poisson) et la severite des dommages (distribution log-normale).
                Le VaR 99.5% represente le seuil de perte qui ne sera depasse que dans 0.5% des cas
                sur une annee.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
