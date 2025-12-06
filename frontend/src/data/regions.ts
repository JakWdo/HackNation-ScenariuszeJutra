/**
 * === DANE REGIONÓW ONZ ===
 *
 * Podział geograficzny według standardu ONZ M49
 * z dodatkowymi organizacjami (UE, NATO, BRICS, etc.)
 */

import { Region, Organization, Sector, Country } from '@/types/regions';

// === SEKTORY ANALIZY ===
export const SECTORS: Sector[] = [
  // Ekonomiczne
  {
    id: 'trade',
    name: 'Handel międzynarodowy',
    nameEn: 'International Trade',
    category: 'economic',
    description: 'Wymiana handlowa, taryfy celne, umowy handlowe',
  },
  {
    id: 'finance',
    name: 'Finanse i bankowość',
    nameEn: 'Finance & Banking',
    category: 'economic',
    description: 'Rynki finansowe, banki centralne, kryzysy finansowe',
  },
  {
    id: 'energy',
    name: 'Energia i surowce',
    nameEn: 'Energy & Resources',
    category: 'economic',
    description: 'Ropa, gaz, OZE, surowce strategiczne',
  },
  {
    id: 'technology',
    name: 'Technologie',
    nameEn: 'Technology',
    category: 'economic',
    description: 'AI, cyberbezpieczeństwo, innowacje, startupy',
  },
  // Polityczne
  {
    id: 'security',
    name: 'Bezpieczeństwo',
    nameEn: 'Security',
    category: 'political',
    description: 'Obronność, sojusze wojskowe, konflikty zbrojne',
  },
  {
    id: 'diplomacy',
    name: 'Dyplomacja',
    nameEn: 'Diplomacy',
    category: 'political',
    description: 'Stosunki bilateralne, negocjacje, traktaty',
  },
  {
    id: 'conflicts',
    name: 'Konflikty i napięcia',
    nameEn: 'Conflicts & Tensions',
    category: 'political',
    description: 'Wojny, spory terytorialne, sankcje',
  },
  {
    id: 'elections',
    name: 'Wybory i polityka wewnętrzna',
    nameEn: 'Elections & Domestic Politics',
    category: 'political',
    description: 'Wybory, zmiany rządów, ruchy polityczne',
  },
  // Społeczne
  {
    id: 'demographics',
    name: 'Demografia',
    nameEn: 'Demographics',
    category: 'social',
    description: 'Struktura ludności, starzenie społeczeństw',
  },
  {
    id: 'migration',
    name: 'Migracje',
    nameEn: 'Migration',
    category: 'social',
    description: 'Przepływy migracyjne, uchodźcy, diaspora',
  },
  {
    id: 'health',
    name: 'Zdrowie publiczne',
    nameEn: 'Public Health',
    category: 'social',
    description: 'Pandemie, systemy ochrony zdrowia',
  },
  {
    id: 'education',
    name: 'Edukacja i nauka',
    nameEn: 'Education & Science',
    category: 'social',
    description: 'Systemy edukacji, badania naukowe, wymiana akademicka',
  },
];

// === REGIONY ONZ ===
export const REGIONS: Region[] = [
  {
    id: 'africa',
    name: 'Afryka',
    nameEn: 'Africa',
    color: '#c9a227',
    subregions: [
      {
        id: 'africa-northern',
        name: 'Afryka Północna',
        nameEn: 'Northern Africa',
        regionId: 'africa',
        countries: ['DZA', 'EGY', 'LBY', 'MAR', 'SDN', 'TUN', 'ESH'],
      },
      {
        id: 'africa-western',
        name: 'Afryka Zachodnia',
        nameEn: 'Western Africa',
        regionId: 'africa',
        countries: ['BEN', 'BFA', 'CPV', 'CIV', 'GMB', 'GHA', 'GIN', 'GNB', 'LBR', 'MLI', 'MRT', 'NER', 'NGA', 'SEN', 'SLE', 'TGO'],
      },
      {
        id: 'africa-central',
        name: 'Afryka Środkowa',
        nameEn: 'Central Africa',
        regionId: 'africa',
        countries: ['AGO', 'CMR', 'CAF', 'TCD', 'COG', 'COD', 'GNQ', 'GAB', 'STP'],
      },
      {
        id: 'africa-eastern',
        name: 'Afryka Wschodnia',
        nameEn: 'Eastern Africa',
        regionId: 'africa',
        countries: ['BDI', 'COM', 'DJI', 'ERI', 'ETH', 'KEN', 'MDG', 'MWI', 'MUS', 'MOZ', 'RWA', 'SYC', 'SOM', 'SSD', 'TZA', 'UGA', 'ZMB', 'ZWE'],
      },
      {
        id: 'africa-southern',
        name: 'Afryka Południowa',
        nameEn: 'Southern Africa',
        regionId: 'africa',
        countries: ['BWA', 'SWZ', 'LSO', 'NAM', 'ZAF'],
      },
    ],
  },
  {
    id: 'americas',
    name: 'Ameryki',
    nameEn: 'Americas',
    color: '#6b2d3c',
    subregions: [
      {
        id: 'americas-northern',
        name: 'Ameryka Północna',
        nameEn: 'Northern America',
        regionId: 'americas',
        countries: ['CAN', 'USA', 'MEX', 'GRL'],
      },
      {
        id: 'americas-central',
        name: 'Ameryka Środkowa',
        nameEn: 'Central America',
        regionId: 'americas',
        countries: ['BLZ', 'CRI', 'SLV', 'GTM', 'HND', 'NIC', 'PAN'],
      },
      {
        id: 'americas-caribbean',
        name: 'Karaiby',
        nameEn: 'Caribbean',
        regionId: 'americas',
        countries: ['ATG', 'BHS', 'BRB', 'CUB', 'DMA', 'DOM', 'GRD', 'HTI', 'JAM', 'KNA', 'LCA', 'VCT', 'TTO'],
      },
      {
        id: 'americas-southern',
        name: 'Ameryka Południowa',
        nameEn: 'South America',
        regionId: 'americas',
        countries: ['ARG', 'BOL', 'BRA', 'CHL', 'COL', 'ECU', 'GUY', 'PRY', 'PER', 'SUR', 'URY', 'VEN'],
      },
    ],
  },
  {
    id: 'asia',
    name: 'Azja',
    nameEn: 'Asia',
    color: '#4a6670',
    subregions: [
      {
        id: 'asia-central',
        name: 'Azja Środkowa',
        nameEn: 'Central Asia',
        regionId: 'asia',
        countries: ['KAZ', 'KGZ', 'TJK', 'TKM', 'UZB'],
      },
      {
        id: 'asia-eastern',
        name: 'Azja Wschodnia',
        nameEn: 'Eastern Asia',
        regionId: 'asia',
        countries: ['CHN', 'HKG', 'JPN', 'PRK', 'KOR', 'MNG', 'TWN'],
      },
      {
        id: 'asia-southeastern',
        name: 'Azja Południowo-Wschodnia',
        nameEn: 'South-Eastern Asia',
        regionId: 'asia',
        countries: ['BRN', 'KHM', 'IDN', 'LAO', 'MYS', 'MMR', 'PHL', 'SGP', 'THA', 'TLS', 'VNM'],
      },
      {
        id: 'asia-southern',
        name: 'Azja Południowa',
        nameEn: 'Southern Asia',
        regionId: 'asia',
        countries: ['AFG', 'BGD', 'BTN', 'IND', 'IRN', 'MDV', 'NPL', 'PAK', 'LKA'],
      },
      {
        id: 'asia-western',
        name: 'Azja Zachodnia (Bliski Wschód)',
        nameEn: 'Western Asia',
        regionId: 'asia',
        countries: ['ARM', 'AZE', 'BHR', 'CYP', 'GEO', 'IRQ', 'ISR', 'JOR', 'KWT', 'LBN', 'OMN', 'PSE', 'QAT', 'SAU', 'SYR', 'TUR', 'ARE', 'YEM'],
      },
    ],
  },
  {
    id: 'europe',
    name: 'Europa',
    nameEn: 'Europe',
    color: '#2c5282',
    subregions: [
      {
        id: 'europe-northern',
        name: 'Europa Północna',
        nameEn: 'Northern Europe',
        regionId: 'europe',
        countries: ['DNK', 'EST', 'FIN', 'ISL', 'IRL', 'LVA', 'LTU', 'NOR', 'SWE', 'GBR'],
      },
      {
        id: 'europe-western',
        name: 'Europa Zachodnia',
        nameEn: 'Western Europe',
        regionId: 'europe',
        countries: ['AUT', 'BEL', 'FRA', 'DEU', 'LIE', 'LUX', 'MCO', 'NLD', 'CHE'],
      },
      {
        id: 'europe-eastern',
        name: 'Europa Wschodnia',
        nameEn: 'Eastern Europe',
        regionId: 'europe',
        countries: ['BLR', 'BGR', 'CZE', 'HUN', 'MDA', 'POL', 'ROU', 'RUS', 'SVK', 'UKR'],
      },
      {
        id: 'europe-southern',
        name: 'Europa Południowa',
        nameEn: 'Southern Europe',
        regionId: 'europe',
        countries: ['ALB', 'AND', 'BIH', 'HRV', 'GRC', 'ITA', 'MKD', 'MLT', 'MNE', 'PRT', 'SMR', 'SRB', 'SVN', 'ESP', 'VAT'],
      },
    ],
  },
  {
    id: 'oceania',
    name: 'Australia i Oceania',
    nameEn: 'Oceania',
    color: '#38a169',
    subregions: [
      {
        id: 'oceania-australasia',
        name: 'Australia i Nowa Zelandia',
        nameEn: 'Australia and New Zealand',
        regionId: 'oceania',
        countries: ['AUS', 'NZL'],
      },
      {
        id: 'oceania-melanesia',
        name: 'Melanezja',
        nameEn: 'Melanesia',
        regionId: 'oceania',
        countries: ['FJI', 'NCL', 'PNG', 'SLB', 'VUT'],
      },
      {
        id: 'oceania-micronesia',
        name: 'Mikronezja',
        nameEn: 'Micronesia',
        regionId: 'oceania',
        countries: ['FSM', 'GUM', 'KIR', 'MHL', 'NRU', 'PLW'],
      },
      {
        id: 'oceania-polynesia',
        name: 'Polinezja',
        nameEn: 'Polynesia',
        regionId: 'oceania',
        countries: ['COK', 'PYF', 'NIU', 'WSM', 'TKL', 'TON', 'TUV'],
      },
    ],
  },
];

// === ORGANIZACJE MIĘDZYNARODOWE ===
export const ORGANIZATIONS: Organization[] = [
  {
    id: 'eu',
    name: 'Unia Europejska',
    nameEn: 'European Union',
    abbreviation: 'UE',
    type: 'political',
    color: '#003399',
    members: ['AUT', 'BEL', 'BGR', 'HRV', 'CYP', 'CZE', 'DNK', 'EST', 'FIN', 'FRA', 'DEU', 'GRC', 'HUN', 'IRL', 'ITA', 'LVA', 'LTU', 'LUX', 'MLT', 'NLD', 'POL', 'PRT', 'ROU', 'SVK', 'SVN', 'ESP', 'SWE'],
  },
  {
    id: 'nato',
    name: 'Organizacja Traktatu Północnoatlantyckiego',
    nameEn: 'North Atlantic Treaty Organization',
    abbreviation: 'NATO',
    type: 'military',
    color: '#004990',
    members: ['ALB', 'BEL', 'BGR', 'CAN', 'HRV', 'CZE', 'DNK', 'EST', 'FIN', 'FRA', 'DEU', 'GRC', 'HUN', 'ISL', 'ITA', 'LVA', 'LTU', 'LUX', 'MNE', 'NLD', 'MKD', 'NOR', 'POL', 'PRT', 'ROU', 'SVK', 'SVN', 'ESP', 'SWE', 'TUR', 'GBR', 'USA'],
  },
  {
    id: 'brics',
    name: 'BRICS',
    nameEn: 'BRICS',
    abbreviation: 'BRICS',
    type: 'economic',
    color: '#d4a017',
    members: ['BRA', 'RUS', 'IND', 'CHN', 'ZAF', 'EGY', 'ETH', 'IRN', 'SAU', 'ARE'],
  },
  {
    id: 'asean',
    name: 'Stowarzyszenie Narodów Azji Południowo-Wschodniej',
    nameEn: 'Association of Southeast Asian Nations',
    abbreviation: 'ASEAN',
    type: 'regional',
    color: '#0066b3',
    members: ['BRN', 'KHM', 'IDN', 'LAO', 'MYS', 'MMR', 'PHL', 'SGP', 'THA', 'VNM'],
  },
  {
    id: 'au',
    name: 'Unia Afrykańska',
    nameEn: 'African Union',
    abbreviation: 'AU',
    type: 'regional',
    color: '#007a33',
    members: ['DZA', 'AGO', 'BEN', 'BWA', 'BFA', 'BDI', 'CMR', 'CPV', 'CAF', 'TCD', 'COM', 'COG', 'COD', 'CIV', 'DJI', 'EGY', 'GNQ', 'ERI', 'SWZ', 'ETH', 'GAB', 'GMB', 'GHA', 'GIN', 'GNB', 'KEN', 'LSO', 'LBR', 'LBY', 'MDG', 'MWI', 'MLI', 'MRT', 'MUS', 'MAR', 'MOZ', 'NAM', 'NER', 'NGA', 'RWA', 'STP', 'SEN', 'SYC', 'SLE', 'SOM', 'ZAF', 'SSD', 'SDN', 'TZA', 'TGO', 'TUN', 'UGA', 'ZMB', 'ZWE'],
  },
  {
    id: 'g7',
    name: 'Grupa Siedmiu',
    nameEn: 'Group of Seven',
    abbreviation: 'G7',
    type: 'economic',
    color: '#1a365d',
    members: ['CAN', 'FRA', 'DEU', 'ITA', 'JPN', 'GBR', 'USA'],
  },
  {
    id: 'g20',
    name: 'Grupa Dwudziestu',
    nameEn: 'Group of Twenty',
    abbreviation: 'G20',
    type: 'economic',
    color: '#2d3748',
    members: ['ARG', 'AUS', 'BRA', 'CAN', 'CHN', 'FRA', 'DEU', 'IND', 'IDN', 'ITA', 'JPN', 'MEX', 'RUS', 'SAU', 'ZAF', 'KOR', 'TUR', 'GBR', 'USA'],
  },
];

// === POMOCNICZE FUNKCJE ===

// Pobierz region po ID
export function getRegionById(id: string): Region | undefined {
  return REGIONS.find(r => r.id === id);
}

// Pobierz subregion po ID
export function getSubregionById(id: string): { region: Region; subregion: typeof REGIONS[0]['subregions'][0] } | undefined {
  for (const region of REGIONS) {
    const subregion = region.subregions.find(s => s.id === id);
    if (subregion) {
      return { region, subregion };
    }
  }
  return undefined;
}

// Pobierz organizację po ID
export function getOrganizationById(id: string): Organization | undefined {
  return ORGANIZATIONS.find(o => o.id === id);
}

// Pobierz wszystkie kraje z regionu
export function getCountriesFromRegion(regionId: string): string[] {
  const region = getRegionById(regionId);
  if (!region) return [];
  return region.subregions.flatMap(s => s.countries);
}

// Sprawdź czy kraj należy do organizacji
export function isCountryInOrganization(countryIso3: string, organizationId: string): boolean {
  const org = getOrganizationById(organizationId);
  return org ? org.members.includes(countryIso3) : false;
}

// Pobierz sektory według kategorii
export function getSectorsByCategory(category: Sector['category']): Sector[] {
  return SECTORS.filter(s => s.category === category);
}