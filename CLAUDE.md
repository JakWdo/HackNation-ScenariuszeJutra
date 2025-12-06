## DANE
(Ciagle uzywany internet_search)
1. Dane scrapowane z internetu (ministerstwa, raporty)
1.5 Zapisac dane
2. Dzielone na sekcje (paragrafy), diagramy itd
3. Chunking
4. Dodane do bazy wektorowe z bogatymi metadanymi jak sektor, kraje, region, kluczowe osoby itd. 
## AGENCI
1.Idzie input od ambasadora (tekstowy, audiowizuale) + Ambasador wybiera checkery (sektory, region -> kraje, wagi)
2. Model orkiestrator (**DSPY**):
    A) Model orkiestrator wyszkuje dokumenty i przekazuje je dalej mniejszym agentom specjalistom.
    B) Model orkiestrator rozdziela zadania i przekazuje je mniejszym agentom i to oni robia wyszukiwane (kazdy jest specjalista od temaatu/regionu) (hybrid search)
3. Ma to byc reakcja łancuchowa. Jeden rozbija sie na regiony, kolejny na kraje, a jeszcze dalej na sektory. Jest to gleboka analiza.
4. Potem jest odwrocenie i od szczegóły dochodzimy do ogółu (PRZY ZACHOWANIU FLOW I MYSLI)
5. Koncowy agent tworzy podsumowanie calosci pracy w formie raportu.
6. Utworzenie 4 wywołan koncowego agenta. Oraz stworznie 4 raportów. 

## Dzialanie systemu
1. Widoczne rozumowanie, idealnie przyklady dokumentów. 
2. 50mln kontkekstu dokumentow na razie (skalowanie do 5mld)
3. Dodanie multimodal.

## Opcjonalnie
1. Dodanie grafu z polaczniemia miedzy dokumentami oraz ich wizualizacja.
2. Multimodalność 