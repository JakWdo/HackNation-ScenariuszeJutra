/**
 * Hook do zarządzania analizą z SSE streaming.
 *
 * Użycie:
 * ```tsx
 * const { isAnalyzing, thoughtSteps, scenarios, startAnalysis } = useAnalysis();
 *
 * await startAnalysis("Analiza wpływu...", { regions: ["EU"], ... });
 * ```
 */
import { useState, useCallback, useRef, useEffect } from 'react';
import {
  sseClient,
  SSEEvent,
  ScenarioReport,
  getAgentType,
  getAgentDisplayName,
} from '@/lib/sse';
import { AnalysisConfig } from '@/types/regions';
import type { ThoughtStep } from '@/components/ui/ChainOfThought';

interface UseAnalysisReturn {
  // Stan
  isAnalyzing: boolean;
  thoughtSteps: ThoughtStep[];
  scenarios: ScenarioReport[];
  error: string | null;
  sessionId: string | null;

  // Akcje
  startAnalysis: (query: string, config: AnalysisConfig) => Promise<void>;
  stopAnalysis: () => void;
  clearResults: () => void;
}

export function useAnalysis(): UseAnalysisReturn {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [thoughtSteps, setThoughtSteps] = useState<ThoughtStep[]>([]);
  const [scenarios, setScenarios] = useState<ScenarioReport[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);

  const stepIdCounter = useRef(0);

  // Cleanup przy unmount
  useEffect(() => {
    return () => {
      sseClient.close();
    };
  }, []);

  /**
   * Mapuje event SSE na ThoughtStep dla ChainOfThought.
   */
  const mapEventToStep = useCallback((event: SSEEvent): ThoughtStep | null => {
    const baseStep = {
      id: String(++stepIdCounter.current),
      timestamp: new Date(event.timestamp || Date.now()),
    };

    switch (event.type) {
      case 'thinking':
        return {
          ...baseStep,
          agent: event.agent || 'unknown',
          agentType: getAgentType(event.agent),
          status: 'thinking' as const,
          title: getAgentDisplayName(event.agent),
          content: event.content || '',
        };

      case 'document':
        return {
          ...baseStep,
          agent: event.agent || 'search',
          agentType: 'orchestrator',
          status: 'complete' as const,
          title: `Znaleziono dokumenty`,
          content: event.content || `Pobrano ${event.docs?.length || 0} dokumentów`,
          documents: event.docs?.map((d) => ({
            title: d.title,
            relevance: d.relevance,
            source: d.source || 'unknown',
            url: d.url,
            credibility: d.credibility,
          })),
        };

      case 'progress':
        return {
          ...baseStep,
          agent: event.agent || 'system',
          agentType: getAgentType(event.agent),
          status: 'analyzing' as const,
          title: getAgentDisplayName(event.agent),
          content: event.content || 'Przetwarzanie...',
        };

      case 'report':
        // Sekcje raportu - wyświetl jako step
        return {
          ...baseStep,
          agent: 'synthesis',
          agentType: 'synthesis',
          status: 'complete' as const,
          title: `Raport: ${event.section || 'Sekcja'}`,
          content: event.content?.substring(0, 200) + '...' || '',
        };

      case 'error':
        return {
          ...baseStep,
          agent: event.agent || 'system',
          agentType: 'orchestrator',
          status: 'error' as const,
          title: 'Błąd',
          content: event.content || 'Wystąpił błąd',
        };

      case 'done':
        return {
          ...baseStep,
          agent: 'system',
          agentType: 'orchestrator',
          status: 'complete' as const,
          title: 'Analiza zakończona',
          content: 'Wszystkie scenariusze zostały wygenerowane.',
        };

      default:
        return null;
    }
  }, []);

  /**
   * Obsługuje event SSE.
   */
  const handleEvent = useCallback(
    (event: SSEEvent) => {
      console.log('[useAnalysis] Event:', event.type, event.agent);

      // Scenariusze idą do osobnego stanu
      if (event.type === 'scenario') {
        const timeframe = (event.timeframe || '12m') as '12m' | '36m';
        const variant = (event.variant || 'positive') as 'positive' | 'negative';
        
        const scenario: ScenarioReport = {
          timeframe,
          variant,
          title: event.title || 'Scenariusz',
          content: event.content || '',
          confidence: event.confidence || 0.5,
        };
        setScenarios((prev) => [...prev, scenario]);
        return;
      }

      // Mapuj na ThoughtStep
      const step = mapEventToStep(event);
      if (step) {
        setThoughtSteps((prev) => {
          // Zaktualizuj poprzedni step tego samego agenta na 'complete'
          const updated = prev.map((s) =>
            s.agent === step.agent && (s.status === 'thinking' || s.status === 'analyzing' || s.status === 'searching')
              ? { ...s, status: 'complete' as const }
              : s
          );
          return [...updated, step];
        });
      }

      // Zakończ analizę
      if (event.type === 'done') {
        setIsAnalyzing(false);
      }
    },
    [mapEventToStep]
  );

  /**
   * Rozpoczyna analizę.
   */
  const startAnalysis = useCallback(
    async (query: string, config: AnalysisConfig) => {
      // Reset stanu
      setIsAnalyzing(true);
      setError(null);
      setThoughtSteps([]);
      setScenarios([]);
      stepIdCounter.current = 0;

      try {
        const id = await sseClient.startAnalysis(
          query,
          config,
          // onEvent callback
          handleEvent,
          // onError callback
          (err) => {
            setError(err.message);
            setIsAnalyzing(false);
          }
        );

        setSessionId(id);
        console.log('[useAnalysis] Started analysis, session:', id);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Nieznany błąd';
        setError(message);
        setIsAnalyzing(false);
        console.error('[useAnalysis] Error starting analysis:', err);
      }
    },
    [handleEvent]
  );

  /**
   * Zatrzymuje analizę.
   */
  const stopAnalysis = useCallback(() => {
    sseClient.close();
    setIsAnalyzing(false);
    console.log('[useAnalysis] Analysis stopped');
  }, []);

  /**
   * Czyści wyniki.
   */
  const clearResults = useCallback(() => {
    setThoughtSteps([]);
    setScenarios([]);
    setError(null);
    setSessionId(null);
    stepIdCounter.current = 0;
  }, []);

  return {
    isAnalyzing,
    thoughtSteps,
    scenarios,
    error,
    sessionId,
    startAnalysis,
    stopAnalysis,
    clearResults,
  };
}