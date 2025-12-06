/**
 * === TYPY DLA REGIONÓW I SEKTORÓW ===
 *
 * Struktura danych dla systemu analizy geopolitycznej
 */

// Poziomy hierarchii geograficznej
export type GeographyLevel = 'continent' | 'region' | 'subregion' | 'country';

// Sektor analizy
export interface Sector {
  id: string;
  name: string;
  nameEn: string;
  category: 'economic' | 'political' | 'social';
  description: string;
}

// Kraj
export interface Country {
  id: string;
  name: string;
  nameEn: string;
  iso2: string;
  iso3: string;
  subregionId: string;
}

// Subregion (np. Europa Północna)
export interface Subregion {
  id: string;
  name: string;
  nameEn: string;
  regionId: string;
  countries: string[]; // ISO3 codes
}

// Region/Kontynent (np. Europa)
export interface Region {
  id: string;
  name: string;
  nameEn: string;
  subregions: Subregion[];
  color?: string;
}

// Organizacja międzynarodowa (UE, NATO, etc.)
export interface Organization {
  id: string;
  name: string;
  nameEn: string;
  abbreviation: string;
  type: 'political' | 'economic' | 'military' | 'regional';
  members: string[]; // ISO3 codes
  color: string;
}

// Stan nawigacji na mapie
export interface MapNavigationState {
  level: GeographyLevel;
  selectedContinent: string | null;
  selectedRegion: string | null;
  selectedSubregion: string | null;
  selectedCountry: string | null;
  hoveredGeography: string | null;
}

// Konfiguracja analizy
export interface AnalysisConfig {
  regions: string[];
  subregions: string[];
  countries: string[];
  organizations: string[];
  sectors: string[];
  weights: Record<string, number>;
}

// Rezultat hover preview
export interface HoverPreviewData {
  id: string;
  name: string;
  type: GeographyLevel | 'organization';
  stats?: {
    countries?: number;
    population?: string;
    gdp?: string;
  };
  position: { x: number; y: number };
}
