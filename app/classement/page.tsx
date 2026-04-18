"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ALL_WILAYAS } from "@/lib/data";
import { MapPin, Search, Filter, AlertTriangle, AlertCircle, CheckCircle } from "lucide-react";

type ZoneFilter = "all" | "III" | "II" | "I";

export default function ClassementPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [zoneFilter, setZoneFilter] = useState<ZoneFilter>("all");

  const filteredWilayas = ALL_WILAYAS.filter((w) => {
    const matchesSearch = w.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesZone = zoneFilter === "all" || w.zone === zoneFilter;
    return matchesSearch && matchesZone;
  });

  // Group by zone
  const zoneIII = ALL_WILAYAS.filter((w) => w.zone === "III");
  const zoneII = ALL_WILAYAS.filter((w) => w.zone === "II");
  const zoneI = ALL_WILAYAS.filter((w) => w.zone === "I");

  const getZoneInfo = (zone: string) => {
    switch (zone) {
      case "III":
        return {
          color: "#e31a1c",
          bgColor: "bg-red-500/10",
          borderColor: "border-red-500/30",
          label: "Zone III - Risque Eleve",
          icon: AlertTriangle,
          description: "Zones a forte activite sismique, historiquement touchees par des seismes majeurs",
        };
      case "II":
        return {
          color: "#ff7f00",
          bgColor: "bg-orange-500/10",
          borderColor: "border-orange-500/30",
          label: "Zone II - Risque Modere",
          icon: AlertCircle,
          description: "Zones a activite sismique moderee, vigilance requise",
        };
      default:
        return {
          color: "#33a02c",
          bgColor: "bg-green-500/10",
          borderColor: "border-green-500/30",
          label: "Zone I - Risque Faible",
          icon: CheckCircle,
          description: "Zones a faible activite sismique",
        };
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-[hsl(var(--foreground))]">
          Classement des Wilayas par Zone Sismique
        </h1>
        <p className="text-[hsl(var(--muted-foreground))] mt-1">
          Classification selon le Reglement Parasismique Algerien (RPA)
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="border-l-4 border-l-red-500">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-[hsl(var(--muted-foreground))]">Zone III (Rouge)</p>
                <p className="text-3xl font-bold text-red-500">{zoneIII.length}</p>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">wilayas a risque eleve</p>
              </div>
              <div className="h-12 w-12 rounded-full bg-red-500/10 flex items-center justify-center">
                <AlertTriangle className="h-6 w-6 text-red-500" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-orange-500">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-[hsl(var(--muted-foreground))]">Zone II (Orange)</p>
                <p className="text-3xl font-bold text-orange-500">{zoneII.length}</p>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">wilayas a risque modere</p>
              </div>
              <div className="h-12 w-12 rounded-full bg-orange-500/10 flex items-center justify-center">
                <AlertCircle className="h-6 w-6 text-orange-500" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-green-500">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-[hsl(var(--muted-foreground))]">Zone I (Vert)</p>
                <p className="text-3xl font-bold text-green-500">{zoneI.length}</p>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">wilayas a risque faible</p>
              </div>
              <div className="h-12 w-12 rounded-full bg-green-500/10 flex items-center justify-center">
                <CheckCircle className="h-6 w-6 text-green-500" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filter */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[hsl(var(--muted-foreground))]" />
          <input
            type="text"
            placeholder="Rechercher une wilaya..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] pl-10 pr-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-[hsl(var(--primary))] transition-all"
          />
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setZoneFilter("all")}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
              zoneFilter === "all"
                ? "bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]"
                : "bg-[hsl(var(--muted))] text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--border))]"
            }`}
          >
            Toutes
          </button>
          <button
            onClick={() => setZoneFilter("III")}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
              zoneFilter === "III"
                ? "bg-red-500 text-white"
                : "bg-red-500/10 text-red-500 hover:bg-red-500/20"
            }`}
          >
            Zone III
          </button>
          <button
            onClick={() => setZoneFilter("II")}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
              zoneFilter === "II"
                ? "bg-orange-500 text-white"
                : "bg-orange-500/10 text-orange-500 hover:bg-orange-500/20"
            }`}
          >
            Zone II
          </button>
          <button
            onClick={() => setZoneFilter("I")}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
              zoneFilter === "I"
                ? "bg-green-500 text-white"
                : "bg-green-500/10 text-green-500 hover:bg-green-500/20"
            }`}
          >
            Zone I
          </button>
        </div>
      </div>

      {/* Wilaya List */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {filteredWilayas.map((wilaya, index) => {
          const zoneInfo = getZoneInfo(wilaya.zone);
          const Icon = zoneInfo.icon;
          return (
            <div
              key={wilaya.code}
              className={`rounded-2xl border ${zoneInfo.borderColor} ${zoneInfo.bgColor} p-4 transition-all hover:shadow-md animate-fade-in`}
              style={{ animationDelay: `${index * 30}ms` }}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div
                    className="h-10 w-10 rounded-xl flex items-center justify-center text-white font-bold text-sm"
                    style={{ backgroundColor: zoneInfo.color }}
                  >
                    {wilaya.code}
                  </div>
                  <div>
                    <h3 className="font-semibold text-[hsl(var(--foreground))]">
                      {wilaya.name}
                    </h3>
                    <p className="text-xs" style={{ color: zoneInfo.color }}>
                      Zone {wilaya.zone}
                    </p>
                  </div>
                </div>
                <Icon className="h-5 w-5" style={{ color: zoneInfo.color }} />
              </div>
            </div>
          );
        })}
      </div>

      {filteredWilayas.length === 0 && (
        <div className="text-center py-12">
          <MapPin className="h-12 w-12 mx-auto text-[hsl(var(--muted-foreground))] mb-4" />
          <p className="text-[hsl(var(--muted-foreground))]">
            Aucune wilaya trouvee pour cette recherche
          </p>
        </div>
      )}

      {/* Zone Details */}
      <div className="space-y-6 mt-8">
        <h2 className="text-2xl font-bold text-[hsl(var(--foreground))]">
          Details par Zone
        </h2>

        {(["III", "II", "I"] as const).map((zone) => {
          const zoneInfo = getZoneInfo(zone);
          const wilayas = ALL_WILAYAS.filter((w) => w.zone === zone);
          const Icon = zoneInfo.icon;

          return (
            <Card key={zone} className={`border-l-4`} style={{ borderLeftColor: zoneInfo.color }}>
              <CardHeader>
                <CardTitle className="flex items-center gap-3">
                  <Icon className="h-6 w-6" style={{ color: zoneInfo.color }} />
                  <span style={{ color: zoneInfo.color }}>{zoneInfo.label}</span>
                  <span className="ml-auto text-sm font-normal text-[hsl(var(--muted-foreground))]">
                    {wilayas.length} wilayas
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-[hsl(var(--muted-foreground))] mb-4">
                  {zoneInfo.description}
                </p>
                <div className="flex flex-wrap gap-2">
                  {wilayas.map((w) => (
                    <span
                      key={w.code}
                      className={`px-3 py-1.5 rounded-full text-sm font-medium ${zoneInfo.bgColor}`}
                      style={{ color: zoneInfo.color }}
                    >
                      {w.name}
                    </span>
                  ))}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
