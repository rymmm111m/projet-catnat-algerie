"use client";

import { useEffect, useState, useCallback } from "react";
import dynamic from "next/dynamic";
import { getWilayaZone, WILAYA_COMMUNES } from "@/lib/data";

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
const Marker = dynamic(
  () => import("react-leaflet").then((mod) => mod.Marker),
  { ssr: false }
);
const Popup = dynamic(
  () => import("react-leaflet").then((mod) => mod.Popup),
  { ssr: false }
);

// Dynamic import for useMap hook
const useMapHook = () => {
  const [mapInstance, setMapInstance] = useState<L.Map | null>(null);
  return { mapInstance, setMapInstance };
};

// Component to control map view - must be inside MapContainer
function MapViewController({ 
  selectedWilaya, 
  geoData,
}: { 
  selectedWilaya: string | null; 
  geoData: GeoJSON.FeatureCollection | null;
}) {
  const [map, setMap] = useState<L.Map | null>(null);

  useEffect(() => {
    // Get the map instance from the parent MapContainer
    const mapContainer = document.querySelector('.leaflet-container');
    if (mapContainer) {
      // @ts-expect-error - Leaflet attaches map instance to the container
      const leafletMap = mapContainer._leaflet_map;
      if (leafletMap) {
        setMap(leafletMap);
      }
    }
  }, []);

  useEffect(() => {
    if (!map || !geoData) return;

    if (selectedWilaya) {
      // Find the selected wilaya feature
      const feature = geoData.features.find(
        (f) => f.properties?.adm1_name?.toUpperCase() === selectedWilaya.toUpperCase()
      );

      if (feature && feature.geometry) {
        // Calculate bounds from the feature
        const L = require("leaflet");
        const geoJsonLayer = L.geoJSON(feature);
        const bounds = geoJsonLayer.getBounds();
        
        if (bounds.isValid()) {
          map.fitBounds(bounds, { 
            padding: [50, 50],
            maxZoom: 10,
            animate: true,
            duration: 0.5
          });
        }
      }
    } else {
      // Reset to Algeria view
      map.setView([28.0, 2.0], 5, { animate: true });
    }
  }, [selectedWilaya, geoData, map]);

  return null;
}

interface AlgeriaMapProps {
  onWilayaSelect?: (wilaya: string) => void;
  selectedWilaya?: string | null;
}

export function AlgeriaMap({ onWilayaSelect, selectedWilaya }: AlgeriaMapProps) {
  const [geoData, setGeoData] = useState<GeoJSON.FeatureCollection | null>(null);
  const [isClient, setIsClient] = useState(false);
  const [communeMarkers, setCommuneMarkers] = useState<Array<{ name: string; lat: number; lng: number }>>([]);
  const [mapKey, setMapKey] = useState(0);

  useEffect(() => {
    setIsClient(true);
    // Load GeoJSON data
    fetch("/dza_admin1.geojson")
      .then((res) => res.json())
      .then((data) => setGeoData(data))
      .catch(console.error);
  }, []);

  // Handle zoom when wilaya is selected
  useEffect(() => {
    if (!isClient || !geoData) return;

    if (selectedWilaya) {
      const communes = WILAYA_COMMUNES[selectedWilaya.toUpperCase()] || [];
      const feature = geoData.features.find(
        (f) => f.properties?.adm1_name?.toUpperCase() === selectedWilaya.toUpperCase()
      );

      if (feature && communes.length > 0) {
        // Get centroid of the wilaya
        const L = require("leaflet");
        const geoJsonLayer = L.geoJSON(feature);
        const center = geoJsonLayer.getBounds().getCenter();
        
        // Generate positions for communes (spread around the center)
        const markers = communes.slice(0, 10).map((name, i) => {
          const angle = (i / Math.min(communes.length, 10)) * 2 * Math.PI;
          const radius = 0.15 + Math.random() * 0.1;
          return {
            name,
            lat: center.lat + Math.sin(angle) * radius * (0.5 + Math.random() * 0.5),
            lng: center.lng + Math.cos(angle) * radius * (0.5 + Math.random() * 0.5),
          };
        });
        setCommuneMarkers(markers);

        // Trigger zoom
        setTimeout(() => {
          const mapContainer = document.querySelector('.leaflet-container');
          if (mapContainer) {
            // @ts-expect-error - Leaflet attaches map instance to the container
            const map = mapContainer._leaflet_map;
            if (map && feature) {
              const geoJsonLayer = L.geoJSON(feature);
              const bounds = geoJsonLayer.getBounds();
              if (bounds.isValid()) {
                map.fitBounds(bounds, { 
                  padding: [50, 50],
                  maxZoom: 10,
                  animate: true
                });
              }
            }
          }
        }, 100);
      } else {
        setCommuneMarkers([]);
      }
    } else {
      setCommuneMarkers([]);
      // Reset to Algeria view
      setTimeout(() => {
        const mapContainer = document.querySelector('.leaflet-container');
        if (mapContainer) {
          // @ts-expect-error - Leaflet attaches map instance to the container
          const map = mapContainer._leaflet_map;
          if (map) {
            map.setView([28.0, 2.0], 5, { animate: true });
          }
        }
      }, 100);
    }
  }, [selectedWilaya, geoData, isClient]);

  const styleFeature = useCallback((feature: GeoJSON.Feature) => {
    const wilayaName = feature.properties?.adm1_name || "";
    const { color } = getWilayaZone(wilayaName);
    const isSelected = selectedWilaya?.toUpperCase() === wilayaName.toUpperCase();

    return {
      fillColor: color,
      weight: isSelected ? 3 : 1,
      opacity: 1,
      color: isSelected ? "#ffffff" : "rgba(255,255,255,0.5)",
      fillOpacity: isSelected ? 0.85 : 0.7,
    };
  }, [selectedWilaya]);

  const onEachFeature = useCallback((feature: GeoJSON.Feature, layer: L.Layer) => {
    const wilayaName = feature.properties?.adm1_name || "";
    const { label } = getWilayaZone(wilayaName);
    const communes = WILAYA_COMMUNES[wilayaName.toUpperCase()] || [];

    layer.bindTooltip(
      `<div class="font-semibold">${wilayaName}</div>
       <div class="text-xs">${label}</div>
       <div class="text-xs mt-1">${communes.length} communes</div>`,
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
  }, [onWilayaSelect, styleFeature]);

  if (!isClient) {
    return (
      <div className="h-[500px] w-full rounded-2xl bg-[hsl(var(--muted))] animate-pulse flex items-center justify-center">
        <span className="text-[hsl(var(--muted-foreground))]">Chargement de la carte...</span>
      </div>
    );
  }

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
        .leaflet-popup-content-wrapper {
          background: hsl(var(--card)) !important;
          border-radius: 12px !important;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        }
        .leaflet-popup-content {
          margin: 12px 16px !important;
          color: hsl(var(--foreground)) !important;
        }
        .leaflet-popup-tip {
          background: hsl(var(--card)) !important;
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
            key={`geojson-${selectedWilaya || "all"}`}
            data={geoData}
            style={styleFeature}
            onEachFeature={onEachFeature}
          />
        )}
        
        {/* Commune markers when wilaya is selected */}
        {selectedWilaya && communeMarkers.map((marker) => (
          <Marker
            key={marker.name}
            position={[marker.lat, marker.lng]}
          >
            <Popup>
              <div className="text-sm">
                <div className="font-semibold">{marker.name}</div>
                <div className="text-xs text-gray-500">{selectedWilaya}</div>
              </div>
            </Popup>
          </Marker>
        ))}
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

      {/* Selected Wilaya Info */}
      {selectedWilaya && (
        <div className="absolute top-4 right-4 z-[1000] bg-[hsl(var(--card))]/95 backdrop-blur-sm rounded-xl p-3 shadow-lg border border-[hsl(var(--border))]">
          <div className="text-xs text-[hsl(var(--muted-foreground))]">Selection active</div>
          <div className="font-semibold text-[hsl(var(--foreground))]">{selectedWilaya}</div>
          <div className="text-xs text-[hsl(var(--primary))]">
            {WILAYA_COMMUNES[selectedWilaya.toUpperCase()]?.length || 0} communes
          </div>
        </div>
      )}
    </div>
  );
}
