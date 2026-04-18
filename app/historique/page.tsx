"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { HISTORICAL_EARTHQUAKES } from "@/lib/data";
import { Calendar, MapPin, Activity, Users, AlertTriangle } from "lucide-react";

export default function HistoriquePage() {
  const sortedEarthquakes = [...HISTORICAL_EARTHQUAKES].sort(
    (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
  );

  const totalDeaths = HISTORICAL_EARTHQUAKES.reduce((sum, eq) => sum + (eq.deaths || 0), 0);
  const avgMagnitude =
    HISTORICAL_EARTHQUAKES.reduce((sum, eq) => sum + eq.magnitude, 0) /
    HISTORICAL_EARTHQUAKES.length;
  const maxMagnitude = Math.max(...HISTORICAL_EARTHQUAKES.map((eq) => eq.magnitude));

  const getMagnitudeColor = (magnitude: number) => {
    if (magnitude >= 7) return "#e31a1c";
    if (magnitude >= 6) return "#ff7f00";
    if (magnitude >= 5) return "#CDDC39";
    return "#33a02c";
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("fr-FR", {
      day: "numeric",
      month: "long",
      year: "numeric",
    });
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-[hsl(var(--foreground))]">
          Historique des Seismes en Algerie
        </h1>
        <p className="text-[hsl(var(--muted-foreground))] mt-1">
          Evenements sismiques majeurs ayant touche le territoire algerien
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-[hsl(var(--primary))]/10 flex items-center justify-center">
                <Activity className="h-5 w-5 text-[hsl(var(--primary))]" />
              </div>
              <div>
                <p className="text-sm text-[hsl(var(--muted-foreground))]">Seismes recenses</p>
                <p className="text-2xl font-bold text-[hsl(var(--foreground))]">
                  {HISTORICAL_EARTHQUAKES.length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-red-500/10 flex items-center justify-center">
                <AlertTriangle className="h-5 w-5 text-red-500" />
              </div>
              <div>
                <p className="text-sm text-[hsl(var(--muted-foreground))]">Magnitude max</p>
                <p className="text-2xl font-bold text-red-500">{maxMagnitude.toFixed(1)}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-orange-500/10 flex items-center justify-center">
                <Activity className="h-5 w-5 text-orange-500" />
              </div>
              <div>
                <p className="text-sm text-[hsl(var(--muted-foreground))]">Magnitude moy.</p>
                <p className="text-2xl font-bold text-orange-500">{avgMagnitude.toFixed(1)}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-[hsl(var(--muted))] flex items-center justify-center">
                <Users className="h-5 w-5 text-[hsl(var(--muted-foreground))]" />
              </div>
              <div>
                <p className="text-sm text-[hsl(var(--muted-foreground))]">Total victimes</p>
                <p className="text-2xl font-bold text-[hsl(var(--foreground))]">
                  {totalDeaths.toLocaleString("fr-FR")}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Timeline */}
      <Card>
        <CardHeader>
          <CardTitle>Chronologie des Evenements</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-[hsl(var(--border))]" />

            <div className="space-y-8">
              {sortedEarthquakes.map((earthquake, index) => {
                const magnitudeColor = getMagnitudeColor(earthquake.magnitude);
                return (
                  <div
                    key={index}
                    className="relative pl-16 animate-fade-in"
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    {/* Timeline dot */}
                    <div
                      className="absolute left-4 top-2 h-5 w-5 rounded-full border-4 border-[hsl(var(--card))]"
                      style={{ backgroundColor: magnitudeColor }}
                    />

                    <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-5 hover:shadow-lg transition-shadow">
                      <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <span
                              className="px-3 py-1 rounded-full text-white text-sm font-bold"
                              style={{ backgroundColor: magnitudeColor }}
                            >
                              M {earthquake.magnitude}
                            </span>
                            <span className="text-[hsl(var(--muted-foreground))] text-sm flex items-center gap-1">
                              <Calendar className="h-4 w-4" />
                              {formatDate(earthquake.date)}
                            </span>
                          </div>

                          <h3 className="text-xl font-semibold text-[hsl(var(--foreground))] flex items-center gap-2">
                            <MapPin className="h-5 w-5" style={{ color: magnitudeColor }} />
                            {earthquake.location}
                          </h3>

                          <p className="text-[hsl(var(--muted-foreground))] mt-2">
                            {earthquake.description}
                          </p>
                        </div>

                        <div className="flex flex-wrap gap-4 lg:flex-col lg:items-end">
                          {earthquake.deaths > 0 && (
                            <div className="bg-red-500/10 rounded-xl px-4 py-2">
                              <p className="text-xs text-red-500 font-medium">Deces</p>
                              <p className="text-lg font-bold text-red-500">
                                {earthquake.deaths.toLocaleString("fr-FR")}
                              </p>
                            </div>
                          )}
                          {earthquake.injuries && earthquake.injuries > 0 && (
                            <div className="bg-orange-500/10 rounded-xl px-4 py-2">
                              <p className="text-xs text-orange-500 font-medium">Blesses</p>
                              <p className="text-lg font-bold text-orange-500">
                                {earthquake.injuries.toLocaleString("fr-FR")}
                              </p>
                            </div>
                          )}
                          <div className="bg-[hsl(var(--muted))] rounded-xl px-4 py-2">
                            <p className="text-xs text-[hsl(var(--muted-foreground))] font-medium">
                              Profondeur
                            </p>
                            <p className="text-lg font-bold text-[hsl(var(--foreground))]">
                              {earthquake.depth} km
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Magnitude Scale Legend */}
      <Card>
        <CardHeader>
          <CardTitle>Echelle de Magnitude</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="flex items-center gap-3 p-3 rounded-xl bg-red-500/10">
              <div className="h-8 w-8 rounded-full bg-red-500" />
              <div>
                <p className="font-semibold text-red-500">7.0+</p>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">Seisme majeur</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 rounded-xl bg-orange-500/10">
              <div className="h-8 w-8 rounded-full bg-orange-500" />
              <div>
                <p className="font-semibold text-orange-500">6.0 - 6.9</p>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">Seisme fort</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 rounded-xl bg-[hsl(var(--accent))]/10">
              <div className="h-8 w-8 rounded-full bg-[hsl(var(--accent))]" />
              <div>
                <p className="font-semibold text-[hsl(var(--accent-foreground))]">5.0 - 5.9</p>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">Seisme modere</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 rounded-xl bg-green-500/10">
              <div className="h-8 w-8 rounded-full bg-green-500" />
              <div>
                <p className="font-semibold text-green-500">{"< 5.0"}</p>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">Seisme leger</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
