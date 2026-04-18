"use client";

import { useState, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { RiskGauge } from "@/components/charts";
import { ALL_WILAYAS, calculateRiskScore, WILAYA_COMMUNES } from "@/lib/data";
import { formatNumber } from "@/lib/utils";
import {
  MapPin,
  Building2,
  DollarSign,
  FileCheck,
  AlertTriangle,
  CheckCircle,
  AlertCircle,
  ChevronDown,
} from "lucide-react";

const PROPERTY_TYPES = [
  "Immobilier (Habitation)",
  "Commercial (Bureaux/Magasins)",
  "Industriel (Usines/Depots)",
];

export default function SouscriptionPage() {
  const [selectedWilaya, setSelectedWilaya] = useState(ALL_WILAYAS[15].name); // ALGER
  const [selectedCommune, setSelectedCommune] = useState("");
  const [propertyType, setPropertyType] = useState(PROPERTY_TYPES[0]);
  const [capital, setCapital] = useState(50_000_000);
  const [isCommuneDropdownOpen, setIsCommuneDropdownOpen] = useState(false);
  const [communeSearchTerm, setCommuneSearchTerm] = useState("");
  const [result, setResult] = useState<{
    score: number;
    premium: number;
    zone: string;
  } | null>(null);

  const selectedWilayaData = ALL_WILAYAS.find((w) => w.name === selectedWilaya);
  const detectedZone = selectedWilayaData?.zone || "I";

  // Get communes for selected wilaya
  const availableCommunes = useMemo(() => {
    return WILAYA_COMMUNES[selectedWilaya.toUpperCase()] || [];
  }, [selectedWilaya]);

  // Filter communes based on search
  const filteredCommunes = useMemo(() => {
    if (!communeSearchTerm) return availableCommunes;
    return availableCommunes.filter((c) =>
      c.toLowerCase().includes(communeSearchTerm.toLowerCase())
    );
  }, [availableCommunes, communeSearchTerm]);

  // Reset commune when wilaya changes
  const handleWilayaChange = (wilaya: string) => {
    setSelectedWilaya(wilaya);
    setSelectedCommune("");
    setCommuneSearchTerm("");
    setResult(null);
  };

  // Map zone to RPA format
  const getRPAZone = (zone: string) => {
    switch (zone) {
      case "III":
        return "III";
      case "II":
        return "IIa";
      default:
        return "I";
    }
  };

  const handleSubmit = () => {
    const rpaZone = getRPAZone(detectedZone);
    const { score, premium } = calculateRiskScore(rpaZone, propertyType, capital);
    setResult({ score, premium, zone: rpaZone });
  };

  const getRiskLevel = (score: number) => {
    if (score < 40)
      return {
        level: "ACCEPTABLE",
        color: "#33a02c",
        bgColor: "bg-green-500/10",
        borderColor: "border-green-500",
        icon: CheckCircle,
        message: "Profil standard. Aucune mesure particuliere requise.",
      };
    if (score < 75)
      return {
        level: "SURVEILLANCE REQUISE",
        color: "#ff7f00",
        bgColor: "bg-orange-500/10",
        borderColor: "border-orange-500",
        icon: AlertCircle,
        message: "Exposition moderee. Application d'une franchise recommandee.",
      };
    return {
      level: "RISQUE ELEVE",
      color: "#e31a1c",
      bgColor: "bg-red-500/10",
      borderColor: "border-red-500",
      icon: AlertTriangle,
      message: "Activite vulnerable en zone sismique. Etude de vulnerabilite obligatoire.",
    };
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-[hsl(var(--foreground))]">
          Module de Souscription Intelligent
        </h1>
        <p className="text-[hsl(var(--muted-foreground))] mt-1">
          Detection automatique de l&apos;alea sismique et ajustement tarifaire selon l&apos;activite
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Form */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileCheck className="h-5 w-5 text-[hsl(var(--primary))]" />
              Informations du Prospect
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Wilaya */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-[hsl(var(--foreground))] flex items-center gap-2">
                <MapPin className="h-4 w-4 text-[hsl(var(--muted-foreground))]" />
                Wilaya du projet
              </label>
              <select
                value={selectedWilaya}
                onChange={(e) => handleWilayaChange(e.target.value)}
                className="w-full rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--primary))] transition-all"
              >
                {ALL_WILAYAS.map((w) => (
                  <option key={w.code} value={w.name}>
                    {w.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Commune - Dynamic Dropdown */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-[hsl(var(--foreground))] flex items-center gap-2">
                <MapPin className="h-4 w-4 text-[hsl(var(--muted-foreground))]" />
                Commune ({availableCommunes.length} disponibles)
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={selectedCommune || communeSearchTerm}
                  onChange={(e) => {
                    setCommuneSearchTerm(e.target.value);
                    setSelectedCommune("");
                    setIsCommuneDropdownOpen(true);
                  }}
                  onFocus={() => setIsCommuneDropdownOpen(true)}
                  placeholder={`Rechercher une commune de ${selectedWilaya}...`}
                  className="w-full rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] px-4 py-3 pr-10 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--primary))] transition-all"
                />
                <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[hsl(var(--muted-foreground))]" />
                
                {isCommuneDropdownOpen && (
                  <div className="absolute z-50 mt-1 w-full rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] shadow-lg max-h-60 overflow-auto">
                    {filteredCommunes.length > 0 ? (
                      filteredCommunes.map((commune) => (
                        <button
                          key={commune}
                          onClick={() => {
                            setSelectedCommune(commune);
                            setCommuneSearchTerm("");
                            setIsCommuneDropdownOpen(false);
                          }}
                          className="w-full px-4 py-2.5 text-left text-sm hover:bg-[hsl(var(--muted))] transition-colors flex items-center gap-2"
                        >
                          <Building2 className="h-3.5 w-3.5 text-[hsl(var(--muted-foreground))]" />
                          {commune}
                        </button>
                      ))
                    ) : (
                      <div className="px-4 py-3 text-sm text-[hsl(var(--muted-foreground))]">
                        Aucune commune trouvee
                      </div>
                    )}
                  </div>
                )}
              </div>
              {selectedCommune && (
                <p className="text-xs text-[hsl(var(--primary))] flex items-center gap-1">
                  <CheckCircle className="h-3 w-3" />
                  Commune selectionnee: {selectedCommune}
                </p>
              )}
            </div>

            {/* Property Type */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-[hsl(var(--foreground))] flex items-center gap-2">
                <Building2 className="h-4 w-4 text-[hsl(var(--muted-foreground))]" />
                Nature du Bien
              </label>
              <select
                value={propertyType}
                onChange={(e) => setPropertyType(e.target.value)}
                className="w-full rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--primary))] transition-all"
              >
                {PROPERTY_TYPES.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </div>

            {/* Capital */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-[hsl(var(--foreground))] flex items-center gap-2">
                <DollarSign className="h-4 w-4 text-[hsl(var(--muted-foreground))]" />
                Capital total a assurer (DZD)
              </label>
              <input
                type="number"
                value={capital}
                onChange={(e) => setCapital(Number(e.target.value))}
                min={0}
                step={10_000_000}
                className="w-full rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--primary))] transition-all"
              />
              <p className="text-xs text-[hsl(var(--muted-foreground))]">
                Valeur actuelle: {formatNumber(capital)} DZD
              </p>
            </div>

            {/* Detected Zone */}
            <div
              className="rounded-xl p-4 flex items-center gap-3"
              style={{
                backgroundColor:
                  detectedZone === "III"
                    ? "#e31a1c15"
                    : detectedZone === "II"
                    ? "#ff7f0015"
                    : "#33a02c15",
                borderLeft: `4px solid ${
                  detectedZone === "III"
                    ? "#e31a1c"
                    : detectedZone === "II"
                    ? "#ff7f00"
                    : "#33a02c"
                }`,
              }}
            >
              <AlertTriangle
                className="h-5 w-5"
                style={{
                  color:
                    detectedZone === "III"
                      ? "#e31a1c"
                      : detectedZone === "II"
                      ? "#ff7f00"
                      : "#33a02c",
                }}
              />
              <div>
                <p className="text-sm text-[hsl(var(--muted-foreground))]">
                  Zone RPA detectee pour {selectedWilaya}
                  {selectedCommune && ` - ${selectedCommune}`}
                </p>
                <p
                  className="font-semibold"
                  style={{
                    color:
                      detectedZone === "III"
                        ? "#e31a1c"
                        : detectedZone === "II"
                        ? "#ff7f00"
                        : "#33a02c",
                  }}
                >
                  Zone {detectedZone}
                </p>
              </div>
            </div>

            {/* Submit Button */}
            <button
              onClick={handleSubmit}
              className="w-full rounded-xl bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] py-3.5 font-semibold hover:opacity-90 transition-opacity"
            >
              Generer le Diagnostic de Souscription
            </button>
          </CardContent>
        </Card>

        {/* Results */}
        <div className="space-y-6">
          {result ? (
            <>
              {/* Risk Gauge */}
              <Card>
                <CardHeader>
                  <CardTitle>Score de Risque</CardTitle>
                </CardHeader>
                <CardContent className="flex justify-center">
                  <RiskGauge score={result.score} />
                </CardContent>
              </Card>

              {/* Analysis */}
              <Card>
                <CardHeader>
                  <CardTitle>Analyse Technique</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Premium */}
                  <div className="rounded-xl bg-[hsl(var(--primary))]/10 p-4">
                    <p className="text-sm text-[hsl(var(--muted-foreground))]">
                      Prime Nette Annuelle
                    </p>
                    <p className="text-3xl font-bold text-[hsl(var(--primary))]">
                      {formatNumber(result.premium)} DZD
                    </p>
                  </div>

                  {/* Risk Level */}
                  {(() => {
                    const riskInfo = getRiskLevel(result.score);
                    const Icon = riskInfo.icon;
                    return (
                      <div
                        className={`rounded-xl p-4 border-l-4 ${riskInfo.bgColor}`}
                        style={{ borderLeftColor: riskInfo.color }}
                      >
                        <div className="flex items-center gap-2 mb-2">
                          <Icon className="h-5 w-5" style={{ color: riskInfo.color }} />
                          <span className="font-bold" style={{ color: riskInfo.color }}>
                            {riskInfo.level}
                          </span>
                        </div>
                        <p className="text-sm text-[hsl(var(--muted-foreground))]">
                          {riskInfo.message}
                        </p>
                      </div>
                    );
                  })()}

                  {/* Details */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="rounded-xl bg-[hsl(var(--muted))] p-4">
                      <p className="text-xs text-[hsl(var(--muted-foreground))]">Zone RPA</p>
                      <p className="text-lg font-semibold text-[hsl(var(--foreground))]">
                        {result.zone}
                      </p>
                    </div>
                    <div className="rounded-xl bg-[hsl(var(--muted))] p-4">
                      <p className="text-xs text-[hsl(var(--muted-foreground))]">Type de Bien</p>
                      <p className="text-lg font-semibold text-[hsl(var(--foreground))]">
                        {propertyType.split(" ")[0]}
                      </p>
                    </div>
                    <div className="rounded-xl bg-[hsl(var(--muted))] p-4">
                      <p className="text-xs text-[hsl(var(--muted-foreground))]">Localisation</p>
                      <p className="text-lg font-semibold text-[hsl(var(--foreground))]">
                        {selectedCommune || selectedWilaya}
                      </p>
                    </div>
                    <div className="rounded-xl bg-[hsl(var(--muted))] p-4">
                      <p className="text-xs text-[hsl(var(--muted-foreground))]">Taux Applique</p>
                      <p className="text-lg font-semibold text-[hsl(var(--foreground))]">
                        {((result.premium / capital) * 100).toFixed(3)}%
                      </p>
                    </div>
                  </div>

                  {/* Summary Card */}
                  <div className="rounded-xl bg-[hsl(var(--muted))]/50 p-4 border border-[hsl(var(--border))]">
                    <h4 className="font-semibold text-[hsl(var(--foreground))] mb-2">Resume du Contrat</h4>
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-[hsl(var(--muted-foreground))]">Wilaya:</span>
                        <span className="font-medium">{selectedWilaya}</span>
                      </div>
                      {selectedCommune && (
                        <div className="flex justify-between">
                          <span className="text-[hsl(var(--muted-foreground))]">Commune:</span>
                          <span className="font-medium">{selectedCommune}</span>
                        </div>
                      )}
                      <div className="flex justify-between">
                        <span className="text-[hsl(var(--muted-foreground))]">Capital Assure:</span>
                        <span className="font-medium">{formatNumber(capital)} DZD</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-[hsl(var(--muted-foreground))]">Prime Annuelle:</span>
                        <span className="font-medium text-[hsl(var(--primary))]">{formatNumber(result.premium)} DZD</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card className="h-full flex items-center justify-center">
              <CardContent className="text-center py-16">
                <div className="h-16 w-16 rounded-full bg-[hsl(var(--muted))] flex items-center justify-center mx-auto mb-4">
                  <FileCheck className="h-8 w-8 text-[hsl(var(--muted-foreground))]" />
                </div>
                <h3 className="text-lg font-semibold text-[hsl(var(--foreground))] mb-2">
                  Aucun diagnostic genere
                </h3>
                <p className="text-sm text-[hsl(var(--muted-foreground))] max-w-xs mx-auto">
                  Remplissez le formulaire et cliquez sur &quot;Generer le Diagnostic&quot; pour voir
                  l&apos;analyse de risque
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
