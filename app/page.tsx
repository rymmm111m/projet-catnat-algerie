"use client";

import { useState } from "react";
import dynamic from "next/dynamic";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MetricCard } from "@/components/metric-card";
import { ZoneBarChart, ZonePieChart, TypeBarChart } from "@/components/charts";
import { ALL_WILAYAS, getWilayaZone } from "@/lib/data";
import { formatNumber } from "@/lib/utils";
import { DollarSign, Shield, TrendingUp, MapPin, ChevronDown, RotateCcw } from "lucide-react";

const AlgeriaMap = dynamic(
  () => import("@/components/algeria-map").then((mod) => mod.AlgeriaMap),
  { ssr: false }
);

// Sample portfolio data
const PORTFOLIO_DATA = {
  totalCapital: 125_000_000_000,
  totalPremium: 2_500_000_000,
  avgRiskRatio: 2.15,
  zoneData: [
    { name: "Zone III (Rouge)", value: 45_000_000_000 },
    { name: "Zone II (Orange)", value: 55_000_000_000 },
    { name: "Zone 0/I (Vert)", value: 25_000_000_000 },
  ],
  typeData: [
    { name: "Habitation", value: 65_000_000_000 },
    { name: "Commercial", value: 35_000_000_000 },
    { name: "Industriel", value: 25_000_000_000 },
  ],
};

export default function CartographiePage() {
  const [selectedWilaya, setSelectedWilaya] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const filteredWilayas = ALL_WILAYAS.filter((w) =>
    w.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleWilayaSelect = (wilaya: string) => {
    setSelectedWilaya(wilaya);
    setSearchTerm(wilaya);
    setIsDropdownOpen(false);
  };

  const handleReset = () => {
    setSelectedWilaya(null);
    setSearchTerm("");
  };

  const selectedWilayaInfo = selectedWilaya
    ? getWilayaZone(selectedWilaya)
    : null;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-[hsl(var(--foreground))]">
            Cartographie des Risques Sismiques
          </h1>
          <p className="text-[hsl(var(--muted-foreground))] mt-1">
            Visualisation du portefeuille CATNAT par zone RPA
          </p>
        </div>

        {/* Search */}
        <div className="flex gap-3">
          <div className="relative w-72">
            <input
              type="text"
              placeholder="Rechercher une wilaya..."
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setIsDropdownOpen(true);
              }}
              onFocus={() => setIsDropdownOpen(true)}
              className="w-full rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] px-4 py-2.5 pr-10 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--primary))] transition-all"
            />
            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[hsl(var(--muted-foreground))]" />
            {isDropdownOpen && searchTerm && (
              <div className="absolute z-50 mt-1 w-full rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] shadow-lg max-h-60 overflow-auto">
                {filteredWilayas.map((w) => (
                  <button
                    key={w.code}
                    onClick={() => handleWilayaSelect(w.name)}
                    className="w-full px-4 py-2.5 text-left text-sm hover:bg-[hsl(var(--muted))] transition-colors flex items-center justify-between"
                  >
                    <span>{w.name}</span>
                    <span
                      className="text-xs px-2 py-0.5 rounded-full"
                      style={{
                        backgroundColor:
                          w.zone === "III"
                            ? "#e31a1c20"
                            : w.zone === "II"
                            ? "#ff7f0020"
                            : "#33a02c20",
                        color:
                          w.zone === "III"
                            ? "#e31a1c"
                            : w.zone === "II"
                            ? "#ff7f00"
                            : "#33a02c",
                      }}
                    >
                      Zone {w.zone}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>
          <button
            onClick={handleReset}
            className="flex items-center gap-2 rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] px-4 py-2.5 text-sm font-medium hover:bg-[hsl(var(--muted))] transition-colors"
          >
            <RotateCcw className="h-4 w-4" />
            Reinitialiser
          </button>
        </div>
      </div>

      {/* Selected Wilaya Banner */}
      {selectedWilaya && selectedWilayaInfo && (
        <div
          className="rounded-2xl p-4 flex items-center gap-4"
          style={{
            backgroundColor: `${selectedWilayaInfo.color}15`,
            borderLeft: `4px solid ${selectedWilayaInfo.color}`,
          }}
        >
          <MapPin style={{ color: selectedWilayaInfo.color }} className="h-5 w-5" />
          <div>
            <span className="font-semibold text-[hsl(var(--foreground))]">
              {selectedWilaya}
            </span>
            <span className="mx-2 text-[hsl(var(--muted-foreground))]">-</span>
            <span style={{ color: selectedWilayaInfo.color }} className="font-medium">
              {selectedWilayaInfo.label}
            </span>
          </div>
        </div>
      )}

      {/* Map and Metrics */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2">
          <AlgeriaMap
            onWilayaSelect={handleWilayaSelect}
            selectedWilaya={selectedWilaya}
          />
        </div>

        <div className="space-y-4">
          <MetricCard
            title="Capital Total Expose"
            value={`${formatNumber(PORTFOLIO_DATA.totalCapital)} DZD`}
            subtitle="Somme des capitaux assures"
            icon={DollarSign}
            variant="primary"
          />
          <MetricCard
            title="Total Primes Nettes"
            value={`${formatNumber(PORTFOLIO_DATA.totalPremium)} DZD`}
            subtitle="Volume de primes collectees"
            icon={Shield}
            variant="success"
          />
          <MetricCard
            title="Ratio de Risque Moyen"
            value={PORTFOLIO_DATA.avgRiskRatio.toFixed(2)}
            subtitle="Prime / Capital x 1000"
            icon={TrendingUp}
            variant="warning"
          />
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Exposition par Zone RPA</CardTitle>
          </CardHeader>
          <CardContent>
            <ZoneBarChart data={PORTFOLIO_DATA.zoneData} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Repartition par Zone</CardTitle>
          </CardHeader>
          <CardContent>
            <ZonePieChart data={PORTFOLIO_DATA.zoneData} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Exposition par Nature du Risque</CardTitle>
          </CardHeader>
          <CardContent>
            <TypeBarChart data={PORTFOLIO_DATA.typeData} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Repartition par Type de Bien</CardTitle>
          </CardHeader>
          <CardContent>
            <ZonePieChart data={PORTFOLIO_DATA.typeData} />
          </CardContent>
        </Card>
      </div>

      {/* Hotspots */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="border-l-4 border-l-red-500">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <span className="text-red-500">Points Chauds</span>
              <span className="text-sm font-normal text-[hsl(var(--muted-foreground))]">
                (Top 3 Sur-concentration)
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {["ALGER", "BOUMERDES", "BLIDA"].map((w, i) => (
                <div
                  key={w}
                  className="flex items-center justify-between p-3 rounded-xl bg-red-500/5 border border-red-500/20"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-lg font-bold text-red-500">#{i + 1}</span>
                    <span className="font-medium">{w}</span>
                  </div>
                  <span className="text-sm text-[hsl(var(--muted-foreground))]">
                    Zone III
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-green-500">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <span className="text-green-500">Opportunites</span>
              <span className="text-sm font-normal text-[hsl(var(--muted-foreground))]">
                (Top 3 Sous-concentration)
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {["TAMANRASSET", "ILLIZI", "TINDOUF"].map((w, i) => (
                <div
                  key={w}
                  className="flex items-center justify-between p-3 rounded-xl bg-green-500/5 border border-green-500/20"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-lg font-bold text-green-500">#{i + 1}</span>
                    <span className="font-medium">{w}</span>
                  </div>
                  <span className="text-sm text-[hsl(var(--muted-foreground))]">
                    Zone I
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
