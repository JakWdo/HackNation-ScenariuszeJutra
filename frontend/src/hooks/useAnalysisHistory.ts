/**
 * Hook do zarządzania historią analiz w localStorage.
 *
 * Zapisuje zakończone analizy i pozwala je przeglądać.
 */
import { useState, useEffect, useCallback } from 'react';
import type { ScenarioReport } from '@/lib/sse';
import type { ThoughtStep } from '@/components/ui/ChainOfThought';
import type { AnalysisConfig } from '@/types/regions';

// === TYPY ===

export interface SavedAnalysis {
  id: string;
  query: string;
  config: AnalysisConfig;
  scenarios: ScenarioReport[];
  thoughtSteps: ThoughtStep[];
  createdAt: string;
  status: 'completed' | 'error';
}

interface UseAnalysisHistoryReturn {
  history: SavedAnalysis[];
  saveAnalysis: (analysis: Omit<SavedAnalysis, 'id' | 'createdAt'>) => void;
  getAnalysis: (id: string) => SavedAnalysis | undefined;
  deleteAnalysis: (id: string) => void;
  clearHistory: () => void;
}

// === STAŁE ===

const STORAGE_KEY = 'sedno_analysis_history';
const MAX_HISTORY_SIZE = 50; // Maksymalna liczba zapisanych analiz

// === POMOCNICZE ===

function generateId(): string {
  return `analysis_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

function loadFromStorage(): SavedAnalysis[] {
  if (typeof window === 'undefined') return [];

  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return [];

    const parsed = JSON.parse(stored);
    if (!Array.isArray(parsed)) return [];

    return parsed;
  } catch (error) {
    console.error('[useAnalysisHistory] Błąd odczytu z localStorage:', error);
    return [];
  }
}

function saveToStorage(history: SavedAnalysis[]): void {
  if (typeof window === 'undefined') return;

  try {
    // Ogranicz rozmiar historii
    const limited = history.slice(0, MAX_HISTORY_SIZE);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(limited));
  } catch (error) {
    console.error('[useAnalysisHistory] Błąd zapisu do localStorage:', error);
  }
}

// === HOOK ===

export function useAnalysisHistory(): UseAnalysisHistoryReturn {
  const [history, setHistory] = useState<SavedAnalysis[]>([]);

  // Załaduj historię przy mount
  useEffect(() => {
    const loaded = loadFromStorage();
    setHistory(loaded);
  }, []);

  // Zapisz analizę
  const saveAnalysis = useCallback((analysis: Omit<SavedAnalysis, 'id' | 'createdAt'>) => {
    const newAnalysis: SavedAnalysis = {
      ...analysis,
      id: generateId(),
      createdAt: new Date().toISOString(),
    };

    setHistory((prev) => {
      const updated = [newAnalysis, ...prev];
      saveToStorage(updated);
      return updated;
    });

    console.log('[useAnalysisHistory] Zapisano analizę:', newAnalysis.id);
  }, []);

  // Pobierz pojedynczą analizę
  const getAnalysis = useCallback((id: string): SavedAnalysis | undefined => {
    return history.find((a) => a.id === id);
  }, [history]);

  // Usuń analizę
  const deleteAnalysis = useCallback((id: string) => {
    setHistory((prev) => {
      const updated = prev.filter((a) => a.id !== id);
      saveToStorage(updated);
      return updated;
    });
    console.log('[useAnalysisHistory] Usunięto analizę:', id);
  }, []);

  // Wyczyść całą historię
  const clearHistory = useCallback(() => {
    setHistory([]);
    saveToStorage([]);
    console.log('[useAnalysisHistory] Wyczyszczono historię');
  }, []);

  return {
    history,
    saveAnalysis,
    getAnalysis,
    deleteAnalysis,
    clearHistory,
  };
}
