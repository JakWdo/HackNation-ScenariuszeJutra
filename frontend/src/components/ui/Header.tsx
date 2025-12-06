'use client';

/**
 * === HEADER - DIPLOMATIC INTELLIGENCE CENTER ===
 *
 * Nagłówek z eleganckim stylem dyplomatycznym:
 * - Logo "SEDNO" w stylu mosiężnej tabliczki
 * - Status systemu
 * - Zegar w stylu stacji dowodzenia
 */

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Activity, Shield, Clock, Compass } from 'lucide-react';

export default function Header() {
  const [time, setTime] = useState<string>('');
  const [date, setDate] = useState<string>('');

  useEffect(() => {
    const updateDateTime = () => {
      const now = new Date();
      setTime(now.toLocaleTimeString('pl-PL', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      }));
      setDate(now.toLocaleDateString('pl-PL', {
        weekday: 'short',
        day: 'numeric',
        month: 'short',
        year: 'numeric'
      }));
    };
    updateDateTime();
    const interval = setInterval(updateDateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="relative z-50 bg-[var(--color-bg-secondary)] border-b border-[var(--color-border)]">
      {/* Górna linia mosiężna */}
      <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-[var(--color-brass)] to-transparent opacity-60" />

      <div className="px-6 py-4 flex items-center justify-between">
        {/* Lewa strona - Logo */}
        <div className="flex items-center gap-6">
          {/* Logo SEDNO */}
          <motion.div
            className="flex items-center gap-3"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
          >
            {/* Ikona kompasu */}
            <div className="relative">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[var(--color-brass)] to-[var(--color-brass-dark)] flex items-center justify-center shadow-lg">
                <Compass className="w-5 h-5 text-[var(--color-bg-deep)]" />
              </div>
              {/* Efekt świecenia */}
              <div className="absolute inset-0 rounded-lg bg-[var(--color-brass)] opacity-20 blur-md" />
            </div>

            {/* Tekst logo */}
            <div>
              <h1 className="text-2xl font-display font-bold tracking-wider text-[var(--color-text-primary)] uppercase">
                Sedno
              </h1>
              <p className="text-[10px] font-mono text-[var(--color-brass)] tracking-[0.2em] uppercase -mt-0.5">
                Intelligence Center
              </p>
            </div>
          </motion.div>

          {/* Separator */}
          <div className="h-8 w-px bg-[var(--color-border-brass)] opacity-30" />

          {/* Status systemu */}
          <motion.div
            className="flex items-center gap-3"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[var(--color-success-glow)] border border-[var(--color-success)]/20">
              <div className="w-2 h-2 rounded-full bg-[var(--color-success)] animate-pulse shadow-[0_0_8px_var(--color-success)]" />
              <span className="text-xs font-medium text-[var(--color-success)]">
                System aktywny
              </span>
            </div>
          </motion.div>
        </div>

        {/* Środek - Tytuł misji (opcjonalny) */}
        <motion.div
          className="hidden lg:flex items-center gap-2"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Shield className="w-4 h-4 text-[var(--color-brass)]" />
          <span className="text-sm font-medium text-[var(--color-text-secondary)]">
            Analiza Geopolityczna
          </span>
          <span className="text-[var(--color-text-muted)]">|</span>
          <span className="text-sm font-medium text-[var(--color-baltic)]">
            Atlantis
          </span>
        </motion.div>

        {/* Prawa strona - Zegar */}
        <motion.div
          className="flex items-center gap-4"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
        >
          {/* Data i czas */}
          <div className="flex items-center gap-3 px-4 py-2 rounded-lg bg-[var(--color-bg-primary)] border border-[var(--color-border)]">
            <Clock className="w-4 h-4 text-[var(--color-brass)]" />
            <div className="flex flex-col items-end">
              <span className="text-lg font-mono font-semibold text-[var(--color-text-primary)] tracking-wider">
                {time}
              </span>
              <span className="text-[10px] font-mono text-[var(--color-text-muted)] uppercase tracking-wider -mt-1">
                {date}
              </span>
            </div>
          </div>

          {/* Wskaźnik aktywności */}
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-[var(--color-bg-primary)] border border-[var(--color-border)]">
            <Activity className="w-4 h-4 text-[var(--color-baltic)]" />
            <div className="flex gap-0.5">
              {[1, 2, 3, 4, 5].map((i) => (
                <motion.div
                  key={i}
                  className="w-1 bg-[var(--color-baltic)]"
                  animate={{
                    height: [4, 12, 4],
                  }}
                  transition={{
                    duration: 0.8,
                    repeat: Infinity,
                    delay: i * 0.1,
                  }}
                  style={{ borderRadius: 1 }}
                />
              ))}
            </div>
          </div>
        </motion.div>
      </div>

      {/* Dolna linia dekoracyjna */}
      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[var(--color-border-brass)] to-transparent opacity-40" />
    </header>
  );
}
