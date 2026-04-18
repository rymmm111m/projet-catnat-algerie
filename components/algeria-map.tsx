"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { getWilayaZone } from "@/lib/data";

const MapContainer = dynamic(
  () => import("react-leaflet").then((mod) => mod.MapContainer),
  { ssr: false }
);
const TileLayer = dynamic(
  () => import("react-leaflet").then((mod) => mod.TileLayer),
  { ssr: false }
);
const GeoJSON = dynamic(
  () => import("react-leaflet").then((mod) => mod.GeoJSON),
  { ssr: false }
);

interface AlgeriaMapProps {
  onWilayaSelect?: (wilaya: string) => void;
  selectedWilaya?: string | null;
}

export function AlgeriaMap({ onWilayaSelect, selectedWilaya }: AlgeriaMapProps) {
  const [geoData, setGeoData] = useState<GeoJSON.FeatureCollection | null>(null);
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
    // Load GeoJSON data
    fetch("/dza_admin1.geojson")
      .then((res) => res.json())
      .then((data) => setGeoData(data))
      .catch(console.error);
  }, []);

  if (!isClient) {
    return (
      <div className="h-[500px] w-full rounded-2xl bg-[hsl(var(--muted))] animate-pulse flex items-center justify-center">
        <span className="text-[hsl(var(--muted-foreground))]">Chargement de la carte...</span>
      </div>
    );
  }

  const styleFeature = (feature: GeoJSON.Feature) => {
    const wilayaName = feature.properties?.adm1_name || "";
    const { color } = getWilayaZone(wilayaName);
    const isSelected = selectedWilaya?.toUpperCase() === wilayaName.toUpperCase();

    return {
      fillColor: color,
      weight: isSelected ? 3 : 1,
      opacity: 1,
      color: isSelected ? "#ffffff" : "rgba(255,255,255,0.5)",
      fillOpacity: isSelected ? 0.9 : 0.7,
    };
  };

  const onEachFeature = (feature: GeoJSON.Feature, layer: L.Layer) => {
    const wilayaName = feature.properties?.adm1_name || "";
    const { label } = getWilayaZone(wilayaName);

    layer.bindTooltip(
      `<div class="font-semibold">${wilayaName}</div><div class="text-xs">${label}</div>`,
      { sticky: true, className: "custom-tooltip" }
    );

    layer.on({
      click: () => {
        if (onWilayaSelect) {
          onWilayaSelect(wilayaName.toUpperCase());
        }
      },
      mouseover: (e) => {
        const target = e.target as L.Path;
        target.setStyle({
          weight: 2,
          fillOpacity: 0.9,
        });
      },
      mouseout: (e) => {
        const target = e.target as L.Path;
        target.setStyle(styleFeature(feature));
      },
    });
  };

  return (
    <div className="relative h-[500px] w-full rounded-2xl overflow-hidden border border-[hsl(var(--border))] shadow-lg">
      <style jsx global>{`
        .custom-tooltip {
          background: hsl(var(--card)) !important;
          border: 1px solid hsl(var(--border)) !important;
          border-radius: 8px !important;
          padding: 8px 12px !important;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        }
        .custom-tooltip .font-semibold {
          color: hsl(var(--foreground));
        }
        .custom-tooltip .text-xs {
          color: hsl(var(--muted-foreground));
        }
        .leaflet-container {
          height: 100%;
          width: 100%;
          border-radius: 1rem;
        }
      `}</style>
      <MapContainer
        center={[28.0, 2.0]}
        zoom={5}
        style={{ height: "100%", width: "100%" }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
        />
        {geoData && (
          <GeoJSON
            key={selectedWilaya || "all"}
            data={geoData}
            style={styleFeature}
            onEachFeature={onEachFeature}
          />
        )}
      </MapContainer>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 z-[1000] bg-[hsl(var(--card))]/95 backdrop-blur-sm rounded-xl p-4 shadow-lg border border-[hsl(var(--border))]">
        <h4 className="text-sm font-semibold mb-2 text-[hsl(var(--foreground))]">Zones RPA</h4>
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded" style={{ backgroundColor: "#e31a1c" }} />
            <span className="text-xs text-[hsl(var(--muted-foreground))]">Zone III - Risque eleve</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded" style={{ backgroundColor: "#ff7f00" }} />
            <span className="text-xs text-[hsl(var(--muted-foreground))]">Zone II - Risque modere</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded" style={{ backgroundColor: "#33a02c" }} />
            <span className="text-xs text-[hsl(var(--muted-foreground))]">Zone I - Risque faible</span>
          </div>
        </div>
      </div>
    </div>
  );
}
