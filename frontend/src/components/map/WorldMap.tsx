'use client';

import { useState, useCallback, memo, useEffect, useRef } from 'react';
import {
  ComposableMap,
  Geographies,
  Geography,
  ZoomableGroup,
} from 'react-simple-maps';
import { motion, AnimatePresence } from 'framer-motion';
import { REGIONS } from '@/data/regions';
import { Plus, Minus, RotateCcw } from 'lucide-react';
import { Card } from '@/components/ui/card';

// TopoJSON mapy świata
const GEO_URL = 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json';

// Mapowanie krajów na regiony
const countryToRegion: Record<string, string> = {};
const countryToSubregion: Record<string, string> = {};

REGIONS.forEach(region => {
  region.subregions.forEach(subregion => {
    subregion.countries.forEach(code => {
      countryToRegion[code] = region.id;
      countryToSubregion[code] = subregion.id;
    });
  });
});

// Widoki regionów
const REGION_VIEWS: Record<string, { center: [number, number]; zoom: number }> = {
  africa: { center: [20, 0], zoom: 2.2 },
  americas: { center: [-80, 10], zoom: 1.6 },
  asia: { center: [100, 30], zoom: 1.8 },
  europe: { center: [15, 52], zoom: 3.5 },
  oceania: { center: [140, -25], zoom: 2.5 },
};

interface TooltipData {
  name: string;
  code: string;
  region: string;
  x: number;
  y: number;
}

interface WorldMapProps {
  onRegionSelect?: (regionId: string) => void;
  onCountrySelect?: (countryCode: string) => void;
  selectedRegions?: string[];
  selectedCountries?: string[];
}

function WorldMap({
  onRegionSelect,
  onCountrySelect,
  selectedRegions = [],
  selectedCountries = [],
}: WorldMapProps) {
  // Ref do kontenera
  const containerRef = useRef<HTMLDivElement>(null);

  // Stan
  const [position, setPosition] = useState<{ center: [number, number]; zoom: number }>({
    center: [0, 20],
    zoom: 1,
  });
  const [tooltip, setTooltip] = useState<TooltipData | null>(null);
  const [hoveredCountry, setHoveredCountry] = useState<string | null>(null);

  // Aktualizacja pozycji tooltipa przy ruchu myszy
  useEffect(() => {
    const handleGlobalMouseMove = (evt: MouseEvent) => {
      if (tooltip) {
        setTooltip(prev => prev ? {
          ...prev,
          x: evt.clientX,
          y: evt.clientY,
        } : null);
      }
    };

    if (tooltip) {
      window.addEventListener('mousemove', handleGlobalMouseMove);
    }

    return () => {
      window.removeEventListener('mousemove', handleGlobalMouseMove);
    };
  }, [tooltip !== null]);

  // Handler kliknięcia na kraj
  const handleClick = useCallback((geo: { properties: { ISO_A3?: string; NAME?: string } }) => {
    const code = geo.properties.ISO_A3;
    if (!code || code === '-99') return;

    const regionId = countryToRegion[code];

    // Jeśli region nie jest jeszcze wybrany, zoom na niego
    if (regionId && REGION_VIEWS[regionId] && !selectedRegions.includes(regionId)) {
      setPosition(REGION_VIEWS[regionId]);
      onRegionSelect?.(regionId);
    } else {
      // Wybierz kraj
      onCountrySelect?.(code);
    }
  }, [selectedRegions, onRegionSelect, onCountrySelect]);

  // Handler hover - wejście na kraj
  const handleMouseEnter = useCallback((
    geo: { properties: { ISO_A3?: string; NAME?: string } },
    evt: React.MouseEvent
  ) => {
    const code = geo.properties.ISO_A3;
    if (!code || code === '-99') return;

    setHoveredCountry(code);
    setTooltip({
      name: geo.properties.NAME || code,
      code,
      region: countryToRegion[code] || 'unknown',
      x: evt.clientX,
      y: evt.clientY,
    });
  }, []);

  const handleMouseLeave = useCallback(() => {
    setHoveredCountry(null);
    setTooltip(null);
  }, []);

  // Reset widoku
  const handleReset = useCallback(() => {
    setPosition({ center: [0, 20], zoom: 1 });
  }, []);

  // Style dla krajów
  const getCountryStyle = useCallback((geo: { properties: { ISO_A3?: string } }) => {
    const code = geo.properties.ISO_A3 || '';
    const regionId = countryToRegion[code];

    const isHovered = hoveredCountry === code;
    const isSelected = selectedCountries.includes(code);
    const isRegionSelected = selectedRegions.includes(regionId);

    // Minimalist Light Theme Colors
    let fill = '#F8FAFC'; // slate-50 (white-ish)
    let stroke = '#E2E8F0'; // slate-200
    let strokeWidth = 0.5;

    if (isSelected) {
      fill = '#192355'; // Brand Dark
      stroke = '#1e293b';
      strokeWidth = 1.5;
    } else if (isRegionSelected) {
      fill = '#BFDBFE'; // blue-200
      stroke = '#93C5FD';
      strokeWidth = 0.75;
    }

    if (isHovered && !isSelected) {
      fill = '#60A5FA'; // blue-400
      stroke = '#3B82F6';
      strokeWidth = 1;
    }

    return {
      default: {
        fill,
        stroke,
        strokeWidth,
        outline: 'none',
        transition: 'all 200ms ease-out',
        cursor: 'pointer',
      },
      hover: {
        fill: isSelected ? '#192355' : '#60A5FA',
        stroke: isSelected ? '#1e293b' : '#3B82F6',
        strokeWidth: 1,
        outline: 'none',
        cursor: 'pointer',
      },
      pressed: {
        fill: '#192355',
        stroke: '#1e293b',
        strokeWidth: 2,
        outline: 'none',
      },
    };
  }, [hoveredCountry, selectedCountries, selectedRegions]);

  return (
    <div className="relative w-full h-full min-h-[500px] bg-white rounded-xl overflow-hidden shadow-sm border border-slate-100">
      
      {/* Nawigacja */}
      <div className="absolute top-6 left-6 z-20 flex items-center gap-3">
        <button
          onClick={handleReset}
          className="flex items-center gap-2 text-sm bg-white/90 backdrop-blur border border-slate-200 px-3 py-1.5 rounded-lg shadow-sm hover:shadow-md transition-all text-slate-600 font-medium"
        >
          <RotateCcw className="w-4 h-4" />
          <span>Reset</span>
        </button>

        {selectedRegions.length > 0 && (
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400 font-medium">Region:</span>
            {selectedRegions.map(id => {
              const region = REGIONS.find(r => r.id === id);
              return (
                <span key={id} className="bg-blue-50 text-blue-600 px-2 py-0.5 rounded border border-blue-100 font-medium text-xs">
                  {region?.name || id}
                </span>
              );
            })}
          </div>
        )}
      </div>

      {/* Zoom controls */}
      <div className="absolute top-6 right-6 z-20 flex flex-col gap-2">
        <button
          onClick={() => setPosition(p => ({ ...p, zoom: Math.min(p.zoom * 1.5, 8) }))}
          className="w-9 h-9 flex items-center justify-center bg-white/90 backdrop-blur border border-slate-200 rounded-lg shadow-sm hover:shadow-md transition-all text-slate-600"
        >
          <Plus className="w-4 h-4" />
        </button>
        <button
          onClick={() => setPosition(p => ({ ...p, zoom: Math.max(p.zoom / 1.5, 1) }))}
          className="w-9 h-9 flex items-center justify-center bg-white/90 backdrop-blur border border-slate-200 rounded-lg shadow-sm hover:shadow-md transition-all text-slate-600"
        >
          <Minus className="w-4 h-4" />
        </button>
      </div>

      {/* Mapa */}
      <ComposableMap
        projection="geoMercator"
        projectionConfig={{
          scale: 140,
          center: [0, 20],
        }}
        style={{ width: '100%', height: '100%', background: 'white' }}
      >
        <ZoomableGroup
          center={position.center}
          zoom={position.zoom}
          onMoveEnd={({ coordinates, zoom }) => {
            setPosition({ center: coordinates as [number, number], zoom });
          }}
          minZoom={1}
          maxZoom={8}
        >
          <Geographies geography={GEO_URL}>
            {({ geographies }) =>
              geographies.map(geo => (
                <Geography
                  key={geo.rsmKey}
                  geography={geo}
                  onClick={() => handleClick(geo)}
                  onMouseEnter={(evt) => handleMouseEnter(geo, evt)}
                  onMouseLeave={handleMouseLeave}
                  style={getCountryStyle(geo)}
                />
              ))
            }
          </Geographies>
        </ZoomableGroup>
      </ComposableMap>

      {/* Tooltip */}
      <AnimatePresence>
        {tooltip && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 10 }}
            transition={{ duration: 0.15, ease: "easeOut" }}
            className="fixed z-50 pointer-events-none"
            style={{
              left: tooltip.x + 15,
              top: tooltip.y - 10,
            }}
          >
            <Card className="px-4 py-3 min-w-[140px] shadow-xl border-slate-200 bg-white/90 backdrop-blur">
              <div className="font-semibold text-slate-800">
                {tooltip.name}
              </div>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-xs font-mono text-slate-400 bg-slate-100 px-1 rounded">
                  {tooltip.code}
                </span>
                {tooltip.region && (
                  <>
                    <span className="text-slate-300">•</span>
                    <span className="text-xs text-blue-500 font-medium">
                      {REGIONS.find(r => r.id === tooltip.region)?.name || tooltip.region}
                    </span>
                  </>
                )}
              </div>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Legend - simplified */}
      <div className="absolute bottom-6 left-6 z-20">
        <Card className="p-3 border-slate-100 shadow-lg bg-white/80 backdrop-blur-md">
          <div className="text-[10px] font-bold uppercase tracking-wider mb-2 text-slate-400">
            Nawigacja
          </div>
          <div className="flex items-center gap-3 text-xs text-slate-500 font-medium">
            <span>Kliknij → Wybierz</span>
            <span className="text-slate-200">|</span>
            <span>Scroll → Zoom</span>
          </div>
        </Card>
      </div>

      {/* Stats */}
      {selectedCountries.length > 0 && (
        <div className="absolute bottom-6 right-6 z-20">
          <Card className="p-4 border-slate-100 shadow-lg bg-white/80 backdrop-blur-md flex flex-col items-center min-w-[100px]">
            <div className="text-[10px] font-bold uppercase tracking-wider mb-1 text-slate-400">
              Wybrano
            </div>
            <div className="text-2xl font-bold text-[#192355]">{selectedCountries.length}</div>
            <div className="text-[10px] text-slate-400 font-medium">krajów</div>
          </Card>
        </div>
      )}
    </div>
  );
}

export default memo(WorldMap);