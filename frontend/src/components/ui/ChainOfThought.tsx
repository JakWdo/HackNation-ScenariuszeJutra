'use client';

/**
 * === PANEL CHAIN OF THOUGHT ===
 *
 * Wizualizacja rozumowania agentów AI w czasie rzeczywistym
 */

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { 
  Brain, 
  Search, 
  Activity, 
  CheckCircle, 
  AlertCircle, 
  Target, 
  Globe, 
  PieChart, 
  Sparkles, 
  FileText, 
  X, 
  Maximize2,
  Clock,
  Cpu
} from 'lucide-react';
import { cn } from '@/lib/utils';

// Typy dla kroków myślenia
export interface ThoughtStep {
  id: string;
  agent: string;
  agentType: 'orchestrator' | 'regional' | 'country' | 'sector' | 'synthesis';
  status: 'thinking' | 'searching' | 'analyzing' | 'complete' | 'error';
  title: string;
  content: string;
  documents?: { title: string; relevance: number }[];
  children?: ThoughtStep[];
  timestamp: Date;
}

interface ChainOfThoughtProps {
  steps: ThoughtStep[];
  isProcessing?: boolean;
}

// Kolory i ikony dla typów agentów
const AGENT_CONFIG: Record<string, { color: string; bg: string; border: string; icon: React.ElementType; label: string }> = {
  orchestrator: { 
    color: 'text-blue-600', 
    bg: 'bg-blue-50', 
    border: 'border-blue-200',
    icon: Target, 
    label: 'Orkiestrator' 
  },
  regional: { 
    color: 'text-amber-600', 
    bg: 'bg-amber-50', 
    border: 'border-amber-200',
    icon: Globe, 
    label: 'Agent Regionalny' 
  },
  country: { 
    color: 'text-cyan-600', 
    bg: 'bg-cyan-50', 
    border: 'border-cyan-200',
    icon: Globe, 
    label: 'Agent Krajowy' 
  },
  sector: { 
    color: 'text-emerald-600', 
    bg: 'bg-emerald-50', 
    border: 'border-emerald-200',
    icon: PieChart, 
    label: 'Agent Sektorowy' 
  },
  synthesis: { 
    color: 'text-purple-600', 
    bg: 'bg-purple-50', 
    border: 'border-purple-200',
    icon: Sparkles, 
    label: 'Synteza' 
  },
};

const STATUS_CONFIG: Record<string, { icon: React.ElementType; label: string; color: string }> = {
  thinking: { icon: Brain, label: 'Myślę...', color: 'text-slate-500' },
  searching: { icon: Search, label: 'Szukam...', color: 'text-blue-500' },
  analyzing: { icon: Activity, label: 'Analizuję...', color: 'text-indigo-500' },
  complete: { icon: CheckCircle, label: 'Zakończone', color: 'text-emerald-500' },
  error: { icon: AlertCircle, label: 'Błąd', color: 'text-red-500' },
};

export default function ChainOfThought({
  steps,
  isProcessing = false,
}: ChainOfThoughtProps) {
  const [selectedStep, setSelectedStep] = useState<ThoughtStep | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll do najnowszego kroku
  useEffect(() => {
    if (containerRef.current && steps.length > 0) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [steps]);

  // Handle closing modal with Escape key
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setSelectedStep(null);
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, []);

  const renderStepCard = (step: ThoughtStep, index: number) => {
    const config = AGENT_CONFIG[step.agentType] || AGENT_CONFIG.orchestrator;
    const statusConfig = STATUS_CONFIG[step.status] || STATUS_CONFIG.thinking;
    const AgentIcon = config.icon;
    const StatusIcon = statusConfig.icon;

    return (
      <motion.div
        key={step.id}
        layoutId={`step-card-${step.id}`}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: index * 0.05 }}
        className="relative group"
      >
        <div 
          onClick={() => setSelectedStep(step)}
          className={cn(
            "relative p-4 rounded-xl border bg-white transition-all cursor-pointer shadow-sm hover:shadow-md",
            config.border,
            "hover:-translate-y-0.5"
          )}
        >
          {/* Ozdobny pasek po lewej */}
          <div className={cn("absolute left-0 top-0 bottom-0 w-1.5 rounded-l-xl", config.bg.replace('50', '500'))} />

          <div className="flex items-start gap-3 pl-2">
            {/* Ikona */}
            <div className={cn("p-2 rounded-lg", config.bg)}>
              <AgentIcon className={cn("w-5 h-5", config.color)} />
            </div>

            {/* Treść nagłówka */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-1">
                <span className={cn("text-[10px] font-bold uppercase tracking-wider", config.color)}>
                  {config.label}
                </span>
                <span className="text-[10px] text-slate-400 flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {step.timestamp.toLocaleTimeString('pl-PL', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                </span>
              </div>
              
              <h3 className="text-sm font-semibold text-slate-800 leading-tight mb-1 truncate pr-6">
                {step.title}
              </h3>

              <div className="flex items-center gap-2 mt-2">
                <div className={cn("flex items-center gap-1.5 text-[11px] font-medium px-2 py-0.5 rounded-full bg-slate-100", statusConfig.color)}>
                  <StatusIcon className="w-3 h-3" />
                  {statusConfig.label}
                </div>
                {step.documents && step.documents.length > 0 && (
                  <div className="flex items-center gap-1 text-[11px] text-slate-500 bg-slate-50 px-2 py-0.5 rounded-full border border-slate-100">
                    <FileText className="w-3 h-3" />
                    {step.documents.length} dok.
                  </div>
                )}
              </div>
            </div>

            {/* Ikona expand (widoczna na hover) */}
            <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity">
              <Maximize2 className="w-4 h-4 text-slate-400" />
            </div>
          </div>

          {/* Podgląd treści */}
          <div className="mt-3 pl-3 pr-2">
            <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed">
              {step.content}
            </p>
          </div>
        </div>
      </motion.div>
    );
  };

  return (
    <>
      {/* GŁÓWNY PANEL */}
      <Card className="flex flex-col h-full bg-slate-50/50 backdrop-blur border-l border-[var(--color-border)] shadow-none rounded-none">
        {/* Header Panelu */}
        <div className="flex items-center justify-between p-4 border-b border-slate-200 bg-white/80">
          <div className="flex items-center gap-2">
            <Cpu className="w-5 h-5 text-indigo-600" />
            <h2 className="text-sm font-bold text-slate-700 tracking-wide uppercase">
              Proces Analizy
            </h2>
          </div>
          <div className="flex items-center gap-2">
            {isProcessing && (
              <span className="flex items-center gap-1.5 px-3 py-1 bg-indigo-50 text-indigo-600 text-[10px] font-bold rounded-full animate-pulse border border-indigo-100">
                <Activity className="w-3 h-3" />
                PRZETWARZANIE
              </span>
            )}
            <span className="text-[10px] font-medium text-slate-400 bg-slate-100 px-2 py-1 rounded-md border border-slate-200">
              {steps.length} KROKÓW
            </span>
          </div>
        </div>

        {/* Lista Kart */}
        <div
          ref={containerRef}
          className="flex-1 overflow-y-auto p-4 space-y-3 scrollbar-thin scrollbar-thumb-slate-200 scrollbar-track-transparent"
        >
          {steps.length === 0 && !isProcessing ? (
            <div className="flex flex-col items-center justify-center h-full text-center py-12 opacity-50">
              <Brain className="w-12 h-12 text-slate-300 mb-3" />
              <p className="text-sm text-slate-500">
                Oczekiwanie na rozpoczęcie<br />procesu analitycznego...
              </p>
            </div>
          ) : steps.length === 0 && isProcessing ? (
            /* Skeleton loading gdy zaczyna się analiza */
            <SkeletonLoader count={3} />
          ) : (
            <>
              {steps.map((step, i) => renderStepCard(step, i))}
              {/* Skeleton podczas ładowania następnego kroku */}
              {isProcessing && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <SkeletonCard />
                </motion.div>
              )}
            </>
          )}
          
          {/* Pusty element na dole, żeby był margines przy scrollu */}
          <div className="h-2" />
        </div>
      </Card>

      {/* MODAL DETALI */}
      <AnimatePresence>
        {selectedStep && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6">
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedStep(null)}
              className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm"
            />

            {/* Modal Window */}
            <motion.div
              layoutId={`step-card-${selectedStep.id}`}
              className="relative w-full max-w-3xl bg-white rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh]"
              initial={{ scale: 0.9, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.95, opacity: 0, y: 10 }}
              transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            >
              {/* Modal Header */}
              <div className={cn(
                "px-6 py-4 border-b flex items-start justify-between bg-gradient-to-r",
                AGENT_CONFIG[selectedStep.agentType]?.bg || 'bg-slate-50',
                "to-white"
              )}>
                <div className="flex items-start gap-4">
                  <div className={cn(
                    "p-3 rounded-xl bg-white shadow-sm border",
                    AGENT_CONFIG[selectedStep.agentType]?.border
                  )}>
                    {(() => {
                      const Icon = AGENT_CONFIG[selectedStep.agentType]?.icon || Brain;
                      return <Icon className={cn("w-6 h-6", AGENT_CONFIG[selectedStep.agentType]?.color)} />;
                    })()}
                  </div>
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className={cn(
                        "text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-white/50 border",
                        AGENT_CONFIG[selectedStep.agentType]?.color,
                        AGENT_CONFIG[selectedStep.agentType]?.border
                      )}>
                        {AGENT_CONFIG[selectedStep.agentType]?.label}
                      </span>
                      <span className="text-xs text-slate-500 font-mono">
                        ID: {selectedStep.agent}
                      </span>
                    </div>
                    <h2 className="text-xl font-bold text-slate-800 leading-snug">
                      {selectedStep.title}
                    </h2>
                  </div>
                </div>
                
                <button
                  onClick={() => setSelectedStep(null)}
                  className="p-2 hover:bg-black/5 rounded-full transition-colors"
                >
                  <X className="w-6 h-6 text-slate-400 hover:text-slate-600" />
                </button>
              </div>

              {/* Modal Content - Scrollable */}
              <div className="flex-1 overflow-y-auto p-6 md:p-8 scrollbar-thin scrollbar-thumb-slate-200">
                {/* Meta info bar */}
                <div className="flex flex-wrap gap-4 mb-6 pb-6 border-b border-slate-100">
                   <div className="flex items-center gap-2 text-sm text-slate-600">
                      <StatusIconWrapper status={selectedStep.status} />
                      <span className="font-medium">
                        Status: {STATUS_CONFIG[selectedStep.status]?.label}
                      </span>
                   </div>
                   <div className="flex items-center gap-2 text-sm text-slate-600">
                      <Clock className="w-4 h-4 text-slate-400" />
                      <span className="font-mono">
                        {selectedStep.timestamp.toLocaleTimeString('pl-PL', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                      </span>
                   </div>
                </div>

                {/* Main Text Content */}
                <div className="prose prose-slate prose-sm max-w-none mb-8">
                  <p className="whitespace-pre-wrap leading-relaxed text-slate-700">
                    {selectedStep.content}
                  </p>
                </div>

                {/* Documents Section */}
                {selectedStep.documents && selectedStep.documents.length > 0 && (
                  <div className="bg-slate-50 rounded-xl p-5 border border-slate-200">
                    <h4 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3 flex items-center gap-2">
                      <Search className="w-3 h-3" />
                      Analizowane źródła
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {selectedStep.documents.map((doc, idx) => (
                        <div 
                          key={idx}
                          className="flex items-center justify-between p-3 bg-white border border-slate-200 rounded-lg hover:border-blue-300 transition-colors group"
                        >
                          <div className="flex items-center gap-3 min-w-0">
                            <FileText className="w-4 h-4 text-slate-400 group-hover:text-blue-500" />
                            <span className="text-sm font-medium text-slate-700 truncate">
                              {doc.title}
                            </span>
                          </div>
                          <span className={cn(
                            "text-xs font-bold px-2 py-0.5 rounded",
                            doc.relevance > 0.8 ? "bg-emerald-100 text-emerald-700" : 
                            doc.relevance > 0.5 ? "bg-amber-100 text-amber-700" : "bg-slate-100 text-slate-600"
                          )}>
                            {Math.round(doc.relevance * 100)}%
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Modal Footer (Optional status bar) */}
              <div className="px-6 py-3 bg-slate-50 border-t border-slate-200 flex justify-between items-center text-xs text-slate-400">
                 <span>System Analizy Geopolitycznej "Sedno"</span>
                 <span>v1.0.0</span>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
}

// Helper component for status icons inside the modal
function StatusIconWrapper({ status }: { status: string }) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.thinking;
  const Icon = config.icon;
  return <Icon className={cn("w-4 h-4", config.color)} />;
}

// Skeleton loading dla karty
function SkeletonCard() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="relative p-4 rounded-xl border border-slate-200 bg-white"
    >
      {/* Pasek po lewej - pulsujący */}
      <div className="absolute left-0 top-0 bottom-0 w-1.5 rounded-l-xl bg-slate-200 animate-pulse" />

      <div className="flex items-start gap-3 pl-2">
        {/* Ikona skeleton */}
        <div className="p-2 rounded-lg bg-slate-100 animate-pulse">
          <div className="w-5 h-5 bg-slate-200 rounded" />
        </div>

        {/* Treść skeleton */}
        <div className="flex-1 space-y-2">
          <div className="flex items-center justify-between">
            <div className="h-3 w-24 bg-slate-200 rounded animate-pulse" />
            <div className="h-3 w-16 bg-slate-100 rounded animate-pulse" />
          </div>
          <div className="h-4 w-3/4 bg-slate-200 rounded animate-pulse" />
          <div className="flex gap-2 mt-2">
            <div className="h-5 w-20 bg-slate-100 rounded-full animate-pulse" />
            <div className="h-5 w-16 bg-slate-100 rounded-full animate-pulse" />
          </div>
        </div>
      </div>

      {/* Podgląd treści skeleton */}
      <div className="mt-3 pl-3 pr-2 space-y-1.5">
        <div className="h-3 w-full bg-slate-100 rounded animate-pulse" />
        <div className="h-3 w-2/3 bg-slate-100 rounded animate-pulse" />
      </div>
    </motion.div>
  );
}

// Skeleton loading dla wielu kart
function SkeletonLoader({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.1 }}
        >
          <SkeletonCard />
        </motion.div>
      ))}
    </div>
  );
}
