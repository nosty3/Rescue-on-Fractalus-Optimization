Dokument badawczy zachowany historycznie. Dawne ścieżki i wyniki dotyczą opisanego eksperymentu; aktualną implementację opisuje docs/OPTYMALIZACJE_PL.md, a wyniki zbiorcze docs/benchmarks/METODA_PL.md (ścieżki od katalogu głównego repozytorium).

# Audyt odtwarzalności pomiarów NTSC

## Zakres

Przeprowadzono 24 kontrolne loty 15-sekundowe bez zmian kodu gry:

- dla każdej wersji 3 starty BOOT w jednym procesie emulatora;
- dla każdej wersji 3 starty BOOT w 3 świeżych procesach;
- dla każdej wersji 2 kontrolne odtworzenia własnego stanu tej samej wersji;
- 8 świeżych startów odtwarzających minimum i maksimum każdej z czterech dawnych grup po 20 prób.

Stany kontrolne nigdy nie przechodziły między wersjami. Próby z odtworzeniem stanu służyły wyłącznie diagnostyce; nie wchodzą do nowych średnich normalnych uruchomień.

## Wynik przy jednakowym czasie START

NTSC, 800XL 64 KB, standardowe dodatki, 3300 klatek wideo do START, zatrzymanie na pierwszym wejściu $A32E, zwolnienie START, 170 klatek rozgrzewki, lot prosto, pomiar na $B516 do domknięcia pierwszego pełnego obrazu po 15 sekundach.

| Wersja | FPS | Liczba zgodnych przebiegów |
|---|---:|---:|
| Oryginał | 5,5680427349 | 8/8 |
| v9 | 7,5152824655 | 8/8 |

Dla każdej wersji osobno zgodne były wszystkie odstępy pomiędzy kolejnymi obrazami, nie tylko średnia FPS. Wszystkie 6 natywnych wejść każdej wersji miało identyczne 32 KB RAM przy $A32E. Nie zaobserwowano zmiany wyniku po zastąpieniu wielokrotnego BOOT nowym procesem emulatora.

Oryginał i v9 wygenerowały przy tym różne tereny. Nie wolno obliczać z tej tabeli czystego przyspieszenia kodu na tej samej mapie.

## Odtworzenie dawnych skrajnych wyników

Wybrano minimum i maksimum osobno dla każdej wersji i każdej dawnej serii (8 przypadków). Każdy przypadek uruchomiono ponownie od początku w nowym procesie emulatora z dawnym czasem START.

We wszystkich 8 przypadkach zgodne były:

- SHA-256 danych terenu $0900–$09FF;
- liczba ukończonych odstępów między obrazami;
- czas całego pomiaru co do jednego taktu emulowanego Atari;
- wynik FPS wynikający z tych dwóch liczb.

Nie stwierdzono błędu licznika ani zależności tych odtworzonych wyników od historii procesu. Wyniki są odtwarzalnymi cechami konkretnych startów. Nie jest to dowód odtworzenia wszystkich 80 dawnych prób ani pełnej poprawności emulatora.

## Wniosek i następny etap

Audyt nie potwierdził podejrzenia, że różnica między dawnymi seriami powstała przez narastający stan procesu. Potwierdził zależność wyniku od konkretnego scenariusza startowego, który daje się odtworzyć. Nie dowodzi jednostajnego losowania wszystkich możliwych map ani zgodności terenu obu ROM-ów.

Następny etap to pilot 20 natywnych startów na wersję, każdorazowo w świeżym procesie, z lotem 60-sekundowym. Punkty 15/30/60 s należą do tego samego lotu i nie są osobnymi niezależnymi próbami. Kolejność wersji jest losowana w zrównoważonych blokach. Rozkład czasu START: jednostajny wybór spośród 3000–3599 klatek menu bez powtarzania czasu w obrębie danej wersji. Jest to jawnie określony zbiór scenariuszy emulatora; wyniku nie należy utożsamiać ze średnią wszystkich możliwych rozgrywek na sprzęcie.

## Pliki

- `audit.json`: 16 przebiegów kontrolnych i ich metadane.
- `old-extremes.json`: 8 odtworzonych dawnych wyników.
- `scripts/ntsc_repro_common.py`: inicjalizacja emulatora, wejście w lot i pomiar.
- `scripts/audit_ntsc_repro.py`: porównanie BOOT, nowych procesów i odtworzenia tej samej wersji.
- `scripts/recheck_ntsc_extremes.py`: odtwarzanie skrajnych dawnych prób.

Pliki pamięci, stanów oraz pełne listy zdarzeń są pomocniczymi danymi lokalnymi do diagnostyki, nie materiałem do publikacji w repozytorium.
