'use client';

/**
 * Panel historii analiz.
 *
 * Wyświetla listę zapisanych analiz z localStorage.
 */
import { memo } from 'react';
import { Clock, Trash2, ChevronRight, X } from 'lucide-react';
import type { SavedAnalysis } from '@/hooks/useAnalysisHistory';
import { cn } from '@/lib/utils';

interface HistoryPanelProps {
  history: SavedAnalysis[];
  onSelect: (analysis: SavedAnalysis) => void;
  onDelete: (id: string) => void;
  onClearAll: () => void;
  onClose: () => void;
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diff = now.getTime() - date.getTime();

  // Mniej niż godzina temu
  if (diff < 60 * 60 * 1000) {
    const minutes = Math.floor(diff / (60 * 1000));
    return `${minutes} min temu`;
  }

  // Mniej niż dzień temu
  if (diff < 24 * 60 * 60 * 1000) {
    const hours = Math.floor(diff / (60 * 60 * 1000));
    return `${hours}h temu`;
  }

  // Wczoraj lub starsze
  return date.toLocaleDateString('pl-PL', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  });
}

const HistoryItem = memo(function HistoryItem({
  analysis,
  onSelect,
  onDelete,
}: {
  analysis: SavedAnalysis;
  onSelect: () => void;
  onDelete: () => void;
}) {
  return (
    <div
      className={cn(
        'group relative p-4 rounded-xl border transition-all cursor-pointer',
        'bg-[var(--color-bg-secondary)] border-[var(--color-border)]',
        'hover:border-[var(--color-cyan)]/50 hover:bg-[var(--color-bg-primary)]'
      )}
      onClick={onSelect}
    >
      {/* Nagłówek */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-[var(--color-text-primary)] line-clamp-2">
            {analysis.query}
          </p>
          <div className="flex items-center gap-2 mt-2 text-xs text-[var(--color-text-muted)]">
            <Clock className="w-3 h-3" />
            <span>{formatDate(analysis.createdAt)}</span>
            <span className="text-[var(--color-border)]">|</span>
            <span>{analysis.scenarios.length} scenariuszy</span>
          </div>
        </div>

        {/* Przycisk usuwania */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
          className="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg text-red-400 hover:bg-red-500/20 transition-all"
          title="Usuń"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>

      {/* Regiony/sektory jako tagi */}
      {analysis.config.regions.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-3">
          {analysis.config.regions.slice(0, 3).map((region) => (
            <span
              key={region}
              className="px-2 py-0.5 text-[10px] rounded-full bg-[var(--color-cyan)]/10 text-[var(--color-cyan)] border border-[var(--color-cyan)]/20"
            >
              {region}
            </span>
          ))}
          {analysis.config.regions.length > 3 && (
            <span className="text-[10px] text-[var(--color-text-muted)]">
              +{analysis.config.regions.length - 3}
            </span>
          )}
        </div>
      )}

      {/* Strzałka */}
      <ChevronRight className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--color-text-muted)] opacity-0 group-hover:opacity-100 transition-opacity" />
    </div>
  );
});

export default function HistoryPanel({
  history,
  onSelect,
  onDelete,
  onClearAll,
  onClose,
}: HistoryPanelProps) {
  return (
    <div className="flex-1 flex flex-col bg-[var(--color-bg-primary)]">
      {/* Nagłówek */}
      <div className="flex items-center justify-between p-4 border-b border-[var(--color-border)]">
        <div>
          <h2 className="text-lg font-semibold text-[var(--color-text-primary)]">
            Historia analiz
          </h2>
          <p className="text-xs text-[var(--color-text-muted)]">
            {history.length} zapisanych analiz
          </p>
        </div>
        <div className="flex items-center gap-2">
          {history.length > 0 && (
            <button
              onClick={onClearAll}
              className="text-xs text-red-400 hover:text-red-300 px-3 py-1.5 rounded-lg hover:bg-red-500/10 transition-colors"
            >
              Wyczyść wszystko
            </button>
          )}
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-[var(--color-bg-secondary)] transition-colors"
          >
            <X className="w-5 h-5 text-[var(--color-text-muted)]" />
          </button>
        </div>
      </div>

      {/* Lista */}
      <div className="flex-1 overflow-y-auto p-4">
        {history.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <Clock className="w-12 h-12 text-[var(--color-text-muted)] mb-4 opacity-50" />
            <p className="text-[var(--color-text-muted)]">Brak zapisanych analiz</p>
            <p className="text-xs text-[var(--color-text-muted)] mt-1">
              Wykonaj analizę, aby zobaczyć ją tutaj
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {history.map((analysis) => (
              <HistoryItem
                key={analysis.id}
                analysis={analysis}
                onSelect={() => onSelect(analysis)}
                onDelete={() => onDelete(analysis.id)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
