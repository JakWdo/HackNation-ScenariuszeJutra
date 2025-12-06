/**
 * === API CLIENT ===
 *
 * Centralny klient do komunikacji z backendem.
 * Używamy axios dla prostoty.
 */

import axios from 'axios';
import {
  AnalyzeRequest,
  AnalyzeResponse,
  RegionCode,
  SourceCode
} from '@/types/schemas';

// Bazowy URL backendu
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Instancja axios z domyślną konfiguracją
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// === FUNKCJE API ===

export async function startAnalysis(request: AnalyzeRequest): Promise<AnalyzeResponse> {
  const response = await api.post('/api/analyze', request);
  return response.data;
}

export async function getSessionStatus(sessionId: string) {
  const response = await api.get(`/api/session/${sessionId}`);
  return response.data;
}

export async function getSessionResult(sessionId: string) {
  const response = await api.get(`/api/session/${sessionId}/result`);
  return response.data;
}

export async function getRegions() {
  const response = await api.get('/api/regions');
  return response.data;
}

export async function getCountries() {
  const response = await api.get('/api/countries');
  return response.data;
}

export async function getSources() {
  const response = await api.get('/api/sources');
  return response.data;
}

export async function healthCheck() {
  const response = await api.get('/health');
  return response.data;
}