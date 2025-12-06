/**
 * Schematy API - odpowiedniki modeli Pydantic z backendu (@schemas/schemas.py).
 */

// === ENUMS ===

export enum RegionCode {
  EU = "EU",
  USA = "USA",
  NATO = "NATO",
  RUSSIA = "RUSSIA",
  ASIA = "ASIA"
}

export enum SourceCode {
  NATO = "NATO",
  EU_COMMISSION = "EU_COMMISSION",
  US_STATE = "US_STATE",
  UK_FCDO = "UK_FCDO",
  CSIS = "CSIS"
}

export enum ReportSectionType {
  POLITICS = "POLITYKA",
  ECONOMY = "GOSPODARKA",
  DEFENSE = "OBRONNOŚĆ",
  SOCIETY = "SPOŁECZEŃSTWO"
}

// === WYNIKI ANALIZY ===

export interface RegionAnalysis {
  region: string;
  summary: string;
  key_findings: string[];
}

export interface CountryAnalysis {
  country?: string | null;
  source: string;
  official_position: string;
  key_statements: string[];
  confidence: number; // default 0.8
}

export interface ExpertAnalysis {
  agent_name: string;
  agent_type: string;
  content: string;
  confidence: number; // default 0.8
}

// === RAPORT ===

export interface ReportSection {
  title: string;
  content: string;
  key_points: string[];
}

export interface FullReport {
  title: string;
  executive_summary: string;
  sections: Record<string, string>;
  generated_at: string; // ISO format
  confidence_score: number; // default 0.0
}

// === API REQUEST/RESPONSE ===

export interface AnalyzeRequest {
  query: string;
  regions?: RegionCode[]; // default [RegionCode.EU]
  countries?: string[]; // ISO codes
  sectors?: ReportSectionType[];
  sources?: SourceCode[];
  weights?: Record<string, number>;
  timeframes?: string[]; // default ["12m", "36m"]
  include_synthesis?: boolean; // default true
}

export interface AnalyzeResponse {
  session_id: string;
  status: string; // default "processing"
  message: string;
}

export interface SessionStatusResponse {
  session_id: string;
  status: string;
  created_at: string;
  query: string;
}

export interface StreamEvent {
  type: string;
  agent?: string | null;
  content: string;
  timestamp?: string | null;

  // Dodatkowe pola dla różnych typów zdarzeń
  query?: string | null;
  docs?: Array<Record<string, any>> | null;
  progress?: number | null;
  section?: string | null;
  timeframe?: string | null;
  variant?: string | null;
  title?: string | null;
  confidence?: number | null;
  session_id?: string | null;
  result?: Record<string, any> | null;
}

// === DOKUMENTY ===

export interface DocumentMetadata {
  source: string;
  date?: string | null;
  region?: string | null;
  country?: string | null;
  url?: string | null;
}

export interface SearchResult {
  content: string;
  metadata: DocumentMetadata;
  relevance_score: number; // default 0.0
}