"use client";

import { useState, useMemo } from "react";
import dynamic from "next/dynamic";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MetricCard } from "@/components/metric-card";
import { ZoneBarChart, ZonePieChart, TypeBarChart } from "@/components/charts";
import { ALL_WILAYAS, getWilayaZone, getCommuneData, WILAYA_COMMUNES } from "@/lib/data";
import { formatNumber } from "@/lib/utils";
import { DollarSign, Shield, TrendingUp, MapPin, ChevronDown, RotateCcw, Building, AlertTriangle, Target } from "lucide-react";

const AlgeriaMap = dynamic(
  () => import("@/components/algeria-map").then((mod) => mod.AlgeriaMap),
  { ssr: false }
);

// Portfolio data for Algeria (national)
const ALGERIA_PORTFOLIO = {
  totalCapital: 125_000_000_000,
  totalPremium: 2_500_000_000,
  avgRiskRatio: 2.15,
  policies: 58420,
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
  topConcentration: ["ALGER", "BOUMERDES", "BLIDA"],
  lowConcentration: ["TAMANRASSET", "ILLIZI", "TINDOUF"],
};

// Wilaya-specific portfolio data
const WILAYA_PORTFOLIO: Record<string, {
  totalCapital: number;
  totalPremium: number;
  avgRiskRatio: number;
  policies: number;
}> = {
  "ALGER": { totalCapital: 45_000_000_000, totalPremium: 850_000_000, avgRiskRatio: 3.2, policies: 15420 },
  "BOUMERDES": { totalCapital: 28_000_000_000, totalPremium: 520_000_000, avgRiskRatio: 3.5, policies: 8750 },
  "BLIDA": { totalCapital: 18_500_000_000, totalPremium: 345_000_000, avgRiskRatio: 2.8, policies: 6230 },
  "ORAN": { totalCapital: 32_000_000_000, totalPremium: 480_000_000, avgRiskRatio: 2.1, policies: 9870 },
  "CONSTANTINE": { totalCapital: 24_000_000_000, totalPremium: 360_000_000, avgRiskRatio: 1.9, policies: 7650 },
  "SETIF": { totalCapital: 16_000_000_000, totalPremium: 240_000_000, avgRiskRatio: 1.7, policies: 5430 },
  "TIPAZA": { totalCapital: 15_000_000_000, totalPremium: 280_000_000, avgRiskRatio: 3.1, policies: 4820 },
  "CHLEF": { totalCapital: 14_500_000_000, totalPremium: 270_000_000, avgRiskRatio: 3.4, policies: 4650 },
  "AIN DEFLA": { totalCapital: 12_000_000_000, totalPremium: 220_000_000, avgRiskRatio: 3.0, policies: 3890 },
  "TIZI OUZOU": { totalCapital: 18_000_000_000, totalPremium: 270_000_000, avgRiskRatio: 2.2, policies: 5720 },
  "BEJAIA": { totalCapital: 15_500_000_000, totalPremium: 235_000_000, avgRiskRatio: 2.0, policies: 4980 },
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

  // Get data based on selection
  const portfolioData = useMemo(() => {
    if (selectedWilaya) {
      const wilayaData = WILAYA_PORTFOLIO[selectedWilaya.toUpperCase()];
      if (wilayaData) {
        return wilayaData;
      }
      // Default data for wilayas not in the list
      return {
        totalCapital: 8_000_000_000,
        totalPremium: 120_000_000,
        avgRiskRatio: 1.5,
        policies: 2500,
      };
    }
    return ALGERIA_PORTFOLIO;
  }, [selectedWilaya]);

  const communeData = useMemo(() => {
    if (selectedWilaya) {
      return getCommuneData(selectedWilaya);
    }
    return null;
  }, [selectedWilaya]);

  // Zone distribution for selected wilaya or all Algeria
  const zoneData = useMemo(() => {
    if (selectedWilaya && selectedWilayaInfo) {
      // For a single wilaya, show its zone as 100%
      const zoneName = selectedWilayaInfo.label;
      return [{ name: zoneName, value: portfolioData.totalCapital }];
    }
    return ALGERIA_PORTFOLIO.zoneData;
  }, [selectedWilaya, selectedWilayaInfo, portfolioData.totalCapital]);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-[hsl(var(--foreground))]">
            {selectedWilaya ? `Wilaya de ${selectedWilaya}` : "Cartographie des Risques Sismiques"}
          </h1>
          <p className="text-[hsl(var(--muted-foreground))] mt-1">
            {selectedWilaya 
              ? `Analyse detaillee du portefeuille CATNAT - ${communeData?.communes.length || 0} communes`
              : "Visualisation du portefeuille CATNAT par zone RPA - 58 Wilayas"
            }
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
            {selectedWilaya ? "Vue nationale" : "Reinitialiser"}
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
          <div className="flex-1">
            <span className="font-semibold text-[hsl(var(--foreground))]">
              {selectedWilaya}
            </span>
            <span className="mx-2 text-[hsl(var(--muted-foreground))]">-</span>
            <span style={{ color: selectedWilayaInfo.color }} className="font-medium">
              {selectedWilayaInfo.label}
            </span>
          </div>
          <div className="flex items-center gap-2 text-sm text-[hsl(var(--muted-foreground))]">
            <Building className="h-4 w-4" />
            <span>{communeData?.communes.length || 0} communes</span>
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
            title={selectedWilaya ? "Capital Expose" : "Capital Total Expose"}
            value={`${formatNumber(portfolioData.totalCapital)} DZD`}
            subtitle={selectedWilaya ? `Wilaya de ${selectedWilaya}` : "Somme des capitaux assures"}
            icon={DollarSign}
            variant="primary"
          />
          <MetricCard
            title={selectedWilaya ? "Primes Nettes" : "Total Primes Nettes"}
            value={`${formatNumber(portfolioData.totalPremium)} DZD`}
            subtitle={selectedWilaya ? `${portfolioData.policies.toLocaleString()} polices actives` : "Volume de primes collectees"}
            icon={Shield}
            variant="success"
          />
          <MetricCard
            title="Ratio de Risque"
            value={portfolioData.avgRiskRatio.toFixed(2)}
            subtitle="Prime / Capital x 1000"
            icon={TrendingUp}
            variant="warning"
          />
        </div>
      </div>

      {/* Communes List for Selected Wilaya */}
      {selectedWilaya && communeData && communeData.communes.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building className="h-5 w-5 text-[hsl(var(--primary))]" />
              Communes de {selectedWilaya} ({communeData.communes.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {communeData.communes.map((commune) => {
                const concentration = communeData.concentrationData.find(c => c.name === commune);
                const bgColor = concentration?.riskLevel === "high" 
                  ? "bg-red-500/10 border-red-500/30 text-red-700 dark:text-red-400"
                  : concentration?.riskLevel === "medium"
                  ? "bg-orange-500/10 border-orange-500/30 text-orange-700 dark:text-orange-400"
                  : "bg-[hsl(var(--muted))] border-[hsl(var(--border))] text-[hsl(var(--foreground))]";
                
                return (
                  <span
                    key={commune}
                    className={`px-3 py-1.5 rounded-lg text-sm border ${bgColor}`}
                  >
                    {commune}
                  </span>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">
              {selectedWilaya ? `Exposition - ${selectedWilaya}` : "Exposition par Zone RPA"}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ZoneBarChart data={zoneData} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">
              {selectedWilaya ? "Classification de la Zone" : "Repartition par Zone"}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ZonePieChart data={zoneData} />
          </CardContent>
        </Card>

        {!selectedWilaya && (
          <>
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Exposition par Nature du Risque</CardTitle>
              </CardHeader>
              <CardContent>
                <TypeBarChart data={ALGERIA_PORTFOLIO.typeData} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Repartition par Type de Bien</CardTitle>
              </CardHeader>
              <CardContent>
                <ZonePieChart data={ALGERIA_PORTFOLIO.typeData} />
              </CardContent>
            </Card>
          </>
        )}
      </div>

      {/* Hotspots */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="border-l-4 border-l-red-500">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              <span className="text-red-500">Points Chauds</span>
              <span className="text-sm font-normal text-[hsl(var(--muted-foreground))]">
                (Top 3 Sur-concentration)
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {(selectedWilaya && communeData?.topConcentration.length 
                ? communeData.topConcentration.map(c => c.name)
                : ALGERIA_PORTFOLIO.topConcentration
              ).map((item, i) => {
                const concentration = selectedWilaya && communeData
                  ? communeData.concentrationData.find(c => c.name === item)
                  : null;
                
                return (
                  <div
                    key={item}
                    className="flex items-center justify-between p-3 rounded-xl bg-red-500/5 border border-red-500/20"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-lg font-bold text-red-500">#{i + 1}</span>
                      <div>
                        <span className="font-medium">{item}</span>
                        {concentration && (
                          <p className="text-xs text-[hsl(var(--muted-foreground))]">
                            {formatNumber(concentration.exposure)} DZD - {concentration.policies} polices
                          </p>
                        )}
                      </div>
                    </div>
                    <span className="text-sm text-[hsl(var(--muted-foreground))]">
                      {selectedWilaya ? "Haute concentration" : "Zone III"}
                    </span>
                  </div>
                );
              })}
              {selectedWilaya && (!communeData?.topConcentration.length) && (
                <p className="text-sm text-[hsl(var(--muted-foreground))] text-center py-4">
                  Pas de donnees de concentration pour cette wilaya
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-green-500">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Target className="h-5 w-5 text-green-500" />
              <span className="text-green-500">Opportunites</span>
              <span className="text-sm font-normal text-[hsl(var(--muted-foreground))]">
                (Top 3 Sous-concentration)
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {(selectedWilaya && communeData?.lowConcentration.length 
                ? communeData.lowConcentration.map(c => c.name)
                : ALGERIA_PORTFOLIO.lowConcentration
              ).map((item, i) => {
                const concentration = selectedWilaya && communeData
                  ? communeData.concentrationData.find(c => c.name === item)
                  : null;

                return (
                  <div
                    key={item}
                    className="flex items-center justify-between p-3 rounded-xl bg-green-500/5 border border-green-500/20"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-lg font-bold text-green-500">#{i + 1}</span>
                      <div>
                        <span className="font-medium">{item}</span>
                        {concentration && (
                          <p className="text-xs text-[hsl(var(--muted-foreground))]">
                            {formatNumber(concentration.exposure)} DZD - {concentration.policies} polices
                          </p>
                        )}
                      </div>
                    </div>
                    <span className="text-sm text-[hsl(var(--muted-foreground))]">
                      {selectedWilaya ? "Faible concentration" : "Zone I"}
                    </span>
                  </div>
                );
              })}
              {selectedWilaya && (!communeData?.lowConcentration.length) && (
                <p className="text-sm text-[hsl(var(--muted-foreground))] text-center py-4">
                  Zones a potentiel de developpement
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
