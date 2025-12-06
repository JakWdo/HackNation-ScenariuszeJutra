/**
 * === SCENARIUSZE JUTRA - LAYOUT ===
 *
 * Główny layout aplikacji z retro-kartograficznym stylem
 */

import type { Metadata, Viewport } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Scenariusze Jutra | System Analizy Geopolitycznej',
  description: 'Zaawansowany system AI do analizy scenariuszy geopolitycznych dla Ministerstwa Spraw Zagranicznych',
  keywords: ['geopolityka', 'analiza', 'AI', 'MSZ', 'scenariusze'],
  authors: [{ name: 'MSZ' }],
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#f4efe4',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pl">
      <head>
        {/* Preconnect do Google Fonts dla szybszego ładowania */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
