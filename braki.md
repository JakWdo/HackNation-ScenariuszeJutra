# Analiza braków w aplikacji "Scenariusze Jutra"

**Data analizy:** 2025-12-06
**Podstawa:** Porównanie z wymaganiami z SCENARIUSZE_JUTRA.md

---

## 1. Braki krytyczne - wymagane przez MSZ

### 1.1 ❌ Brak warstwy tagowania jednostek informacji

**Wymaganie (pkt 9):**
> Poszczególne jednostki informacji (np. cena ropy w dacie X lub nałożenie embarga na produkty Y przez kraj Z) powinny być otagowane. Narzędzie powinno wskazywać, w jaki sposób poszczególne informacje prowadzą do konkretnych wniosków i które informacje traktowane są priorytetowo (i dlaczego).

**Obecny stan:**
- Chain of Thought pokazuje kroki rozumowania, ale **nie taguje** konkretnych jednostek informacji
- Brak możliwości kliknięcia w "cenę ropy" i zobaczenia skąd pochodzi ta informacja
- Brak wizualizacji priorytetyzacji informacji

**Potrzebne:**
- Panel "Tagged Information Units" z interaktywną listą wszystkich wyekstrahowanych faktów
- Każdy tag powinien pokazywać: źródło, data, wpływ na scenariusz (waga), powiązane wnioski
- Wizualizacja typu "knowledge graph" pokazująca połączenia między tagami

---

### 1.2 ❌ Brak szczegółowej ścieżki rozumowania z linkami do źródeł

**Wymaganie (pkt 9):**
> Narzędzie powinno w tej warstwie wskazywać, w jaki sposób poszczególne informacje prowadzą do konkretnych wniosków [...] oraz ścieżkę prowadzącą z poszczególnych wniosków lub grup wniosków do rekomendacji.

**Obecny stan:**
- ChainOfThought pokazuje kroki, ale nie **konkretne źródła**
- Pole `documents` w ThoughtStep ma tylko `title` i `relevance`, brak `url`, `snippet`, `date_published`
- Brak wizualizacji "Od dokumentu X → przez wniosek Y → do rekomendacji Z"

**Potrzebne:**
- Rozbudowany typ `Document` z pełnymi metadanymi
- Panel "Reasoning Path Viewer" - interaktywna wizualizacja typu flowchart
- Możliwość kliknięcia w każdy krok i zobaczenia pełnego kontekstu

---

### 1.3 ⚠️ Brak wizualizacji danych liczbowych i wykresów

**Wymaganie (pkt 3):**
> Materiał końcowy ma mieć postać tekstu (może być z danymi liczbowymi i wykresami graficznymi)

**Obecny stan:**
- ReportPanel renderuje tylko tekst markdown
- Brak wsparcia dla wykresów (liniowych, słupkowych, kołowych)
- Brak tabel z danymi liczbowymi

**Potrzebne:**
- Integracja z biblioteką wykresów (np. Recharts, Chart.js)
- Parser markdown rozszerzony o składnię dla wykresów
- Komponent `DataVisualization` dla tabel i wykresów

---

### 1.4 ❌ Brak mechanizmu ochrony przed "data poisoning"

**Wymaganie (pkt 9 - Bonus):**
> Mechanizm uodporniający narzędzie na „data poisoning", czyli celowe zanieczyszczanie ogólnodostępnych danych przez nieprzychylnych aktorów

**Obecny stan:**
- Brak walidacji wiarygodności źródeł
- Brak mechanizmu wykrywania sprzecznych informacji
- Brak systemu reputacji źródeł

**Potrzebne:**
- Panel "Source Credibility" z oceną wiarygodności każdego źródła
- Algorytm wykrywania anomalii w danych
- Mechanizm cross-referencingu źródeł
- UI pokazujący ostrzeżenia o potencjalnie "zatrутych" danych

---

### 1.5 ❌ Brak eksportu PDF (funkcjonalny)

**Wymaganie (pkt 4):**
> Tekst zgodny z opisem w punkcie 3

**Obecny stan:**
- Przycisk "Eksportuj PDF" istnieje w ReportPanel, ale **nie działa**
- Brak biblioteki do generowania PDF
- Brak stylowania dla wersji drukowanej

**Potrzebne:**
- Integracja z `react-pdf` lub `jspdf`
- Template PDF z logo MSZ, nagłówkami, stopkami
- Eksport z zachowaniem wykresów i tabel

---

## 2. Braki ważne - wpływ na użyteczność

### 2.1 ⚠️ Brak onboardingu i pomocy kontekstowej

**Problem:**
- Nowy użytkownik nie wie od czego zacząć
- Brak wyjaśnienia co to są "wagi", "regiony", "sektory"
- Brak przykładowych promptów

**Potrzebne:**
- Komponent `Onboarding` z krokami (tour aplikacji)
- Tooltips z wyjaśnieniami przy każdym parametrze
- Panel "Example Queries" z gotowymi scenariuszami
- Link do dokumentacji / help center

---

### 2.2 ❌ Brak panelu kontekstu "Atlantis"

**Problem:**
- Użytkownik nie widzi dla kogo robi analizę
- Brak przypomnienia cech państwa Atlantis (28mln ludności, Bałtyk, etc.)
- Analiza w próżni bez kontekstu

**Potrzebne:**
- Sidebar/Panel "Atlantis Profile" ze wszystkimi cechami z wymagań
- Możliwość edycji profilu (dla innych państw w przyszłości)
- Wizualizacja mapy z lokalizacją Atlantis
- Kluczowe wskaźniki (GDP, populacja, armia) w formie kart

---

### 2.3 ❌ Brak wizualizacji grafu powiązań dokumentów

**Problem:**
- Dokumenty są listowane płasko
- Brak wizualizacji jak dokumenty się ze sobą łączą
- Trudno zrozumieć strukturę wiedzy

**Potrzebne:**
- Komponent `DocumentGraph` z wizualizacją typu force-directed graph
- Każdy dokument = node, powiązanie = edge
- Kolor nodeów = typ źródła (ministerstwo, think tank, giełda)
- Grubość edge'ów = siła powiązania

---

### 2.4 ⚠️ Brak szczegółowego podglądu źródeł

**Problem:**
- W ChainOfThought widać tylko `title` i `relevance`
- Brak snippet'u tekstu
- Brak linku do pełnego dokumentu
- Brak daty publikacji

**Potrzebne:**
- Modal `DocumentDetails` z pełnymi metadanymi
- Snippet (200-300 znaków) z highlighted query terms
- Link do oryginalnego źródła (jeśli publiczne)
- Data publikacji, autor, typ źródła

---

### 2.5 ❌ Brak progress bar dla całej analizy

**Problem:**
- ChainOfThought pokazuje poszczególne kroki, ale nie całość
- Użytkownik nie wie ile jeszcze zostało (10%? 90%?)
- Brak szacowanego czasu zakończenia

**Potrzebne:**
- Progress bar w Header lub jako sticky element
- Etapy: "Wyszukiwanie (25%)" → "Analiza regionalna (50%)" → "Synteza (75%)" → "Scenariusze (100%)"
- ETA (estimated time remaining)

---

### 2.6 ⚠️ Brak trybu porównawczego scenariuszy

**Problem:**
- Użytkownik może oglądać tylko 1 scenariusz na raz
- Trudno porównać "12m pozytywny" vs "12m negatywny"
- Brak side-by-side view

**Potrzebne:**
- Przycisk "Porównaj scenariusze" w ReportPanel
- Layout 2-kolumnowy dla porównania
- Highlight różnic między scenariuszami
- Tabela porównawcza kluczowych wskaźników

---

### 2.7 ❌ Brak wizualizacji wag parametrów

**Problem:**
- Slidery w AnalysisSidebar są OK, ale brak graficznej prezentacji
- Użytkownik nie widzi łącznego rozkładu wag
- Trudno zidentyfikować czy wagi sumują się do 100%

**Potrzebne:**
- Wykres kołowy pokazujący rozkład wag
- Walidacja: ostrzeżenie jeśli suma != 100%
- Panel "Weight Summary" z top 3 najważniejszymi parametrami

---

### 2.8 ⚠️ Brak zaawansowanego filtrowania historii

**Problem:**
- HistoryPanel pokazuje tylko listę chronologiczną
- Brak filtrowania po dacie, regionie, statusie
- Brak wyszukiwania po treści query

**Potrzebne:**
- Search bar w HistoryPanel
- Filtry: data, region, sektor, status (completed/failed)
- Sortowanie: najnowsze, najstarsze, najczęściej używane
- Grupowanie po dniu/tygodniu

---

### 2.9 ❌ Brak możliwości komentowania/annotacji raportów

**Problem:**
- Użytkownik nie może dodać notatek do raportu
- Brak współpracy zespołowej (dyskusja nad raportem)
- Analiza jest "read-only"

**Potrzebne:**
- System komentarzy przypiętych do fragmentów tekstu
- Sidebar `Annotations` z listą wszystkich notatek
- Możliwość udostępnienia raportu z komentarzami
- Oznaczanie fragmentów jako "do weryfikacji"

---

### 2.10 ❌ Brak eksportu do innych formatów

**Problem:**
- Tylko "Kopiuj do schowka" i niedziałający "Eksportuj PDF"
- Brak DOCX (format preferowany przez urzędników)
- Brak XML, JSON (dla dalszego przetwarzania)

**Potrzebne:**
- Przycisk "Eksportuj jako..." z opcjami: PDF, DOCX, XML, JSON, HTML
- Template DOCX z stylami MSZ
- JSON z pełną strukturą (scenariusze + metadata + chain of thought)

---

## 3. Braki funkcjonalności rozszerzających (pkt 9)

### 3.1 ❌ Brak wsparcia dla multimodalności

**Wymaganie (pkt 9):**
> możliwość rozszerzenia poddawanych analizie materiałów poza dane tekstowe - o dane graficzne, audio i wideo (jpg, gif, tif, pdf, docx, txt, xml, mp3, mp4, wave, cdr, ai, psd)

**Obecny stan:**
- PromptPanel ma `accept=".pdf,.doc,.docx,.txt,.csv,.json"` ale tylko tekstowe
- Brak preview attachments (zdjęć, PDF)
- Brak OCR dla obrazów
- Brak transkrypcji audio/video

**Potrzebne:**
- Komponent `AttachmentPreview` dla różnych typów plików
- Integracja z OCR API (dla PDF, obrazów)
- Integracja z Speech-to-Text (dla mp3, mp4)
- Wizualizacja typu "media gallery" dla załączników

---

### 3.2 ❌ Brak możliwości backcasting

**Wymaganie (pkt 9):**
> wielowariantowość metody analitycznej - zmiana konfiguracji działania narzędzia skutkująca zmianą metody analitycznej, np. poprzez zastosowanie prognozowania wstecznego (backcasting)

**Obecny stan:**
- Tylko forecasting (od teraz → przyszłość)
- Brak trybu backcasting (od przyszłości → teraz)

**Potrzebne:**
- Toggle w PromptPanel: "Forecasting" vs "Backcasting"
- W trybie backcasting: użytkownik definiuje "desired future state"
- Analiza generuje kroki od przyszłości do teraźniejszości
- Wizualizacja odwróconej timeline

---

### 3.3 ❌ Brak zaawansowanych parametrów geograficznych

**Wymaganie (pkt 9):**
> możliwość zawężania danych wejściowych na podstawie takich parametrów, jak rejestracja domeny publikującej dane w krajach o określonej liczbie ludności, określonych zasobach wody, określonej liczbie dni nasłonecznienia lub dni wietrznych, posiadających/nieposiadających dostęp do morza, posiadających/nieposiadających broń jądrową, posiadających/nieposiadających zasoby paliw kopalnych

**Obecny stan:**
- AnalysisSidebar ma tylko: Regiony, Organizacje, Sektory, Wagi
- Brak filtrów: populacja, dostęp do morza, broń jądrowa, zasoby

**Potrzebne:**
- Rozbudowa AnalysisSidebar o sekcję "Advanced Filters"
- Slidery dla: populacja (min-max), zasoby wody, nasłonecznienie
- Checkboxy dla: dostęp do morza, broń jądrowa, paliwa kopalne
- Filtr "Domain origin" (domena .gov, .org, .com)

---

### 3.4 ❌ Brak trybu offline/containerized

**Wymaganie (pkt 9):**
> możliwość pracy narzędzia na danych zamkniętych (kontenery) – z odłączeniem od sieci publicznej

**Obecny stan:**
- Aplikacja wymaga połączenia z internetem
- Brak trybu offline
- Brak możliwości pracy na danych lokalnych

**Potrzebne:**
- Toggle "Offline Mode" w Settings
- LocalStorage/IndexedDB dla cache'owania danych
- Możliwość importu "data package" (ZIP z dokumentami)
- Informacja o statusie offline/online w Header

---

### 3.5 ❌ Brak wielojęzyczności UI

**Wymaganie (pkt 5):**
> Narzędzie musi umożliwiać przetwarzanie dużych zbiorów danych tekstowych w języku polskim i angielskim.

**Obecny stan:**
- UI tylko po polsku
- Brak i18n (internationalization)
- Wszystkie napisy hardcoded

**Potrzebne:**
- Integracja z `react-i18next` lub `next-intl`
- Przycisk zmiany języka w Header (PL/EN)
- Tłumaczenia dla wszystkich komponentów
- Locale-aware formatowanie dat, liczb

---

### 3.6 ❌ Brak dashboardu z metrykami

**Problem:**
- Brak widoku "big picture"
- Użytkownik nie widzi statystyk użycia
- Brak metrycznych KPI (czas analizy, liczba dokumentów, success rate)

**Potrzebne:**
- Komponent `Dashboard` jako dodatkowy widok
- Metryki: liczba analiz (dziś/tydzień/miesiąc), średni czas, top regiony
- Wykresy trendów w czasie
- Ranking najczęściej analizowanych krajów/sektorów

---

### 3.7 ❌ Brak systemu uprawnień/ról

**Problem:**
- Brak logowania
- Każdy ma dostęp do wszystkiego
- Brak kontroli dostępu (admin, analyst, viewer)

**Potrzebne:**
- System logowania (OAuth, SAML dla MSZ)
- Role: Admin, Senior Analyst, Analyst, Viewer
- Uprawnienia: kto może tworzyć analizy, eksportować, usuwać
- Audit log (kto co zrobił)

---

### 3.8 ❌ Brak wersjonowania raportów

**Problem:**
- Każda nowa analiza nadpisuje poprzednią (jeśli ten sam query)
- Brak historii zmian
- Niemożność powrotu do starszej wersji

**Potrzebne:**
- System wersjonowania (v1, v2, v3...)
- Widok "Version History" dla każdego raportu
- Diff viewer (porównanie wersji)
- Możliwość przywrócenia starszej wersji

---

### 3.9 ❌ Brak współpracy zespołowej

**Problem:**
- Aplikacja dla single user
- Brak współdzielenia raportów
- Brak wsparcia dla pracy zespołowej

**Potrzebne:**
- Przycisk "Udostępnij" w ReportPanel
- Możliwość generowania linku share (z uprawnieniami)
- System komentarzy (jak Google Docs)
- Real-time collaboration (pokazywanie kto obecnie ogląda raport)

---

## 4. Drobne problemy UX/UI

### 4.1 ⚠️ Brak dark mode

**Problem:**
- Tylko light theme
- Zmienne `--color-bg-deep` są zdefiniowane ale nieużywane
- Brak toggle theme w UI

**Potrzebne:**
- Toggle "Light/Dark" w Header
- Wykorzystanie CSS variables dla theme switching
- Zapisywanie preferencji użytkownika w localStorage

---

### 4.2 ⚠️ Brak responsywności mobilnej

**Problem:**
- Layout 3-kolumnowy (Sidebar | Mapa | CoT) nie działa na małych ekranach
- Brak breakpointów dla mobile/tablet

**Potrzebne:**
- Media queries dla <768px, <1024px
- Collapsible sidebars na mobile
- Bottom sheet dla ChainOfThought na mobile

---

### 4.3 ⚠️ Brak keyboard shortcuts

**Problem:**
- Wszystko wymaga klikania
- Brak skrótów klawiszowych
- Niska produktywność dla power users

**Potrzebne:**
- Shortcuts: Ctrl+K (search), Ctrl+N (nowa analiza), Esc (zamknij modal)
- Panel "Keyboard Shortcuts" (Ctrl+?)
- Podpowiedzi skrótów w tooltipach

---

### 4.4 ⚠️ Brak loading states dla długich operacji

**Problem:**
- ChainOfThought pokazuje skeleton, ale pozostałe komponenty nie
- Brak feedback podczas ładowania mapy

**Potrzebne:**
- Skeleton screens dla wszystkich komponentów
- Spinner z % postępu
- Komunikaty "Ładowanie danych z 15 ministerstw..."

---

### 4.5 ⚠️ Brak obsługi błędów z retry

**Problem:**
- Gdy analiza failuje, tylko czerwony banner "⚠️ {error}"
- Brak możliwości retry
- Brak szczegółów błędu

**Potrzebne:**
- Error boundary z przyjaznym komunikatem
- Przycisk "Spróbuj ponownie"
- Accordion z technical details (stack trace) dla adminów
- Link do support/help

---

## 5. Braki backendowe (wymaga weryfikacji)

**Uwaga:** Te braki dotyczą backendu, który nie był przedmiotem analizy kodu frontendu, ale wynikają z wymagań:

### 5.1 ❓ Skalowalność do 5 mld słów

**Wymaganie:** analiza 50mln słów (podstawa) → 5mld słów (docelowo)

**Do weryfikacji:**
- Czy backend radzi sobie z 50mln słów?
- Jaka infrastruktura do 5mld?
- Czy są bottlenecki?

---

### 5.2 ❓ Wsparcie dla 30 języków

**Wymaganie:** Rozszerzenie do 50 krajów / 30 języków

**Do weryfikacji:**
- Obecnie tylko PL/EN?
- Jakie modele NLP?
- Czy łatwo dodać nowy język?

---

### 5.3 ❓ Bezpieczeństwo prompts

**Wymaganie (pkt 5):**
> Żaden użytkownik sieci internetowej niezalogowany do domeny MSZ nie może mieć wglądu do promptów wysyłanych do chmur obliczeniowych

**Do weryfikacji:**
- Czy prompty są szyfrowane?
- Czy są logowane?
- Kto ma dostęp do logów?

---

### 5.4 ❓ Pamięć 10 promptów

**Wymaganie (pkt 5):**
> Powinno posiadać opcję pamięci 10 ostatnich promptów i ich rezultatów

**Obecny stan:**
- `useAnalysisHistory` zapisuje do localStorage
- Brak limitu 10 (może być więcej lub mniej)

**Do weryfikacji:**
- Czy backend cachuje rezultaty?
- Jak długo trzyma w pamięci?

---

## 6. Podsumowanie - priorytety

### 🔴 Krytyczne (blocker dla wdrożenia):
1. Tagowanie jednostek informacji
2. Szczegółowa ścieżka rozumowania z źródłami
3. Funkcjonalny eksport PDF
4. Mechanizm data poisoning protection
5. Wizualizacja danych liczbowych/wykresów

### 🟡 Ważne (znaczący wpływ na użyteczność):
6. Onboarding i help
7. Panel kontekstu "Atlantis"
8. Graf powiązań dokumentów
9. Progress bar całej analizy
10. Porównywanie scenariuszy
11. Wizualizacja wag
12. Zaawansowane filtrowanie historii

### 🟢 Nice to have (rozszerzenia):
13. Multimodalność (obrazy, audio, video)
14. Backcasting
15. Zaawansowane filtry geograficzne
16. Tryb offline
17. Wielojęzyczność UI
18. Dashboard z metrykami
19. System uprawnień
20. Wersjonowanie i współpraca

---

## 7. Rekomendacje implementacyjne

### Faza 1: MVP+ (1-2 tygodnie)
- ✅ Tagowanie jednostek informacji
- ✅ Funkcjonalny PDF export
- ✅ Onboarding
- ✅ Panel Atlantis
- ✅ Progress bar

### Faza 2: Core Features (2-3 tygodnie)
- ✅ Ścieżka rozumowania z pełnymi źródłami
- ✅ Wykresy i dane liczbowe
- ✅ Graf dokumentów
- ✅ Porównywanie scenariuszy
- ✅ Wizualizacja wag

### Faza 3: Advanced (3-4 tygodnie)
- ✅ Data poisoning protection
- ✅ Multimodalność
- ✅ Backcasting
- ✅ Zaawansowane filtry
- ✅ Eksport do DOCX/XML

### Faza 4: Enterprise (4-6 tygodni)
- ✅ System uprawnień i ról
- ✅ Wersjonowanie
- ✅ Współpraca zespołowa
- ✅ Tryb offline
- ✅ Dashboard i analytics

---

**Koniec analizy**

*Plik wygenerowany automatycznie przez analizę kodu frontendu vs. wymagania z SCENARIUSZE_JUTRA.md*
