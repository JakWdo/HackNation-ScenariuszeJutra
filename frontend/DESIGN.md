# Scenariusze Jutra - Frontend Design System

## Przegląd

System analizy geopolitycznej dla Ministerstwa Spraw Zagranicznych. Interfejs w stylu **Minimalist Dark Dashboard** - czysty, nowoczesny, z zaokrąglonymi panelami i głębokimi cieniami.

---

## Estetyka: Minimalist Dark Dashboard

### Inspiracje
- Modern SaaS Dashboards
- Floating UI elements
- Deep focus interfaces

### Paleta kolorów

```css
/* Tła */
--color-bg-primary: #0a0a0f      /* Główne tło */
--color-bg-secondary: #192355    /* Panele (Header, Sidebar) */

/* Akcenty */
--color-cyan: #00d4ff            /* Główny akcent */

/* Tekst */
--color-text-primary: #ffffff    /* Główny tekst */
--color-text-muted: #94a3b8      /* Wyciszony */

/* Cienie */
--shadow-floating: 0 25px 50px -12px rgba(0, 0, 0, 0.5)
```

### Typografia

```css
--font-display: 'Space Grotesk'  /* Logo, Nagłówki */
--font-body: 'Inter'             /* Interfejs */
--font-mono: 'JetBrains Mono'    /* Dane, czas */
```

### Kluczowe elementy stylu

1. **Floating Panels** - Elementy (Header, Sidebar) są "oderwane" od krawędzi, z dużymi marginesami i zaokrągleniami.
2. **Rounded Corners** - Mocne zaokrąglenia (2xl/3xl) dla kluczowych paneli.
3. **Clean Look** - Brak zbędnych obramowań i dekoracji. Skupienie na treści.
4. **Deep Shadows** - Wyraźne cienie budujące głębię.

---

## Struktura layoutu

```
┌────────────────────────────────────────────────────────────────────────┐
│   [ HEADER (Floating) ]                                                │
│   sedno                                                      HH:MM     │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│   ┌─────────────┐    ┌─────────────────────────────────────────────┐   │
│   │             │    │                                             │   │
│   │  SIDEBAR    │    │                 MAPA                        │   │
│   │  (Floating) │    │                                             │   │
│   │             │    │                                             │   │
│   │  Parametry  │    │                                             │   │
│   │             │    │                                             │   │
│   │             │    │          [ PROMPT PANEL ]                   │   │
│   │             │    │                                             │   │
│   └─────────────┘    └─────────────────────────────────────────────┘   │
│                                                                        │
│                      (Brak stopki systemowej)                          │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Komponenty

### 1. Header (`components/ui/Header.tsx`)

**Styl:**
- Floating (marginesy, zaokrąglone rogi dolne/wszystkie)
- Minimalistyczny
- Cień rzucany na mapę

**Zawiera:**
- Logo tekstowe: **sedno** (lowercase, bold)
- Aktualny czas (prawa strona)

---

### 2. Sidebar - Panel Analizy (`components/sidebar/AnalysisSidebar.tsx`)

**Styl:**
- Floating (marginesy, zaokrąglone rogi)
- Czysty, bez zbędnych linii podziału
- Dopasowany kolorystycznie do Headera

**Zawiera:**
- Rozwijane sekcje parametrów (Regiony, Organizacje, Sektory, Wagi)
- Przycisk "Uruchom analizę" (duży, czytelny)
- **Usunięto:** Statystyki (REG/ORG/SEK/KRA) dla czystszego wyglądu.

---

### 3. Mapa Świata (`components/map/WorldMap.tsx`)

**Technologia:** react-simple-maps + framer-motion

**Elementy UI na mapie:**
- Przycisk Reset
- Badge wyboru
- Zoom controls
- (Elementy te unoszą się nad mapą)

---

### 4. Panel Promptu Ambasadora (`components/ui/PromptPanel.tsx`)

**Styl:**
- Zintegrowany z głównym widokiem
- Minimalistyczny input

---

### 5. Chain of Thought (`components/ui/ChainOfThought.tsx`)

**Funkcja:**
- Wizualizacja procesu myślowego agentów AI
- Panel boczny (prawy)

---

## Technologie

| Technologia | Wersja | Zastosowanie |
|-------------|--------|--------------|
| Next.js | 14.0.4 | Framework React |
| TypeScript | 5.3.3 | Typowanie |
| Tailwind CSS | 3.4.0 | Style |
| Framer Motion | 12.x | Animacje |
| react-simple-maps | 3.0.0 | Mapa SVG |

---

## Uruchomienie

```bash
cd frontend
npm install
npm run dev
# http://localhost:3000
```