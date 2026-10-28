> ARCHIWUM: up38 zastąpiono wydaniem v11. Ten oryginalny XEX ma potwierdzony błąd blokujący ukończenie poziomu (adresy melodii). Użyj poprawionego XEX v11 z ../../optimized%20version/. Poniżej zachowano historyczny opis autorów.

# Rescue on Fractalus! up38

[English](README.md) · [Polski](README_PL.md)

up38 to szybsza wersja Rescue on Fractalus! na Atari XL/XE, zbudowana na **v10.1 od nosty3**
(github.com/nosty3/Rescue-on-Fractalus-Optimization). Rysuje fraktalne góry o ok. 38% szybciej niż oryginalna
gra w PAL i o ok. 41% szybciej w NTSC. Obraz jest taki sam, bajt w bajt.

Pracę wykonał Claude Opus 5.5 (Anthropic) z małą ekipą agentów AI, dla Solo. Podziękowania dla nosty3: jego
v10.1, jego metoda pomiaru i opublikowane wyniki były punktem wyjścia i miarą.

## Wyniki

Pomiar metodą nosty3: 155 automatycznych lotów po 60 sekund na wersję i system TV, te same momenty startu,
to samo ustawienie emulatora.

| System | Oryginał | v10.1 (nosty3) | up38 | up38 do oryginału |
|---|---:|---:|---:|---:|
| PAL | 6,44 FPS | 7,64 FPS (+18,5%) | **8,94 FPS** | **+38,7%** |
| NTSC | 5,80 FPS | 6,94 FPS (+19,5%) | **8,17 FPS** | **+40,7%** |

FPS oznacza tu liczbę gotowych obrazów terenu na sekundę. Przed pomiarem up38 zmierzyliśmy jeszcze raz
oryginał i v10.1: wszystkie 620 lotów wyszło identycznie z liczbami opublikowanymi przez nosty3.

**Czy gra robi się trudniejsza?** Nie. Logika gry (energia, wrogowie, piloci) chodzi na własnym zegarze
25 Hz, niezależnie od liczby obrazów. Zmierzyliśmy procedurę energii: ok. 25 wywołań na sekundę zarówno
w oryginale, jak i w up38. To ta sama gra, tylko częściej rysowana.

## Pliki

- `bin/fractalus_up38.car` - cartridge (XEGS 128 KB, CART typ 14). Działa w Altirrze i na kartach flash, które
  czytają `.car` (SIDE3, Ultimate Cart, AVG Cart, The!Cart).
- `bin/fractalus_up38.rom` - to samo jako surowy ROM (wybrać XEGS 128 KB).
- `bin/up38_from_v10.1.ips` - łatka do ROM-u v10.1 od nosty3.
- `bin/fractalus_up38_320k-1mb.xex` - wersja na Atari z rozszerzoną pamięcią (320K Rambo, 576K albo 1 MB), dla
  ładujących pliki przez SIO2SD albo FujiNet. Ta sama prędkość co cartridge. Na sprzęcie z za małą pamięcią
  pokazuje komunikat zamiast się wysypać. Rzadkie sceny (lądowanie, ratowanie pilota, kosmita, koniec gry)
  sprawdziliśmy na razie tylko analizą: jeśli coś się tam wysypie, prosimy o zgłoszenie sceny.

## Co się zmieniło, po ludzku

1. **Kasowanie zaczyna się wcześniej.** Gra czekała na następną ramkę, zanim wyczyściła ukryty bufor. Teraz
   zaczyna, gdy tylko promień telewizora minie góry. (+2,1%)
2. **Zasłonięte kawałki gór są pomijane.** Góry powstają przez wielokrotne dzielenie odcinków. Jeśli cała
   gałąź tego dzielenia wylądowałaby za narysowanymi już górami, jest pomijana. (+4,0%)
3. **Krótsze przerwanie.** Milczące kanały dźwięku są szybko pomijane, wskaźnik w kokpicie rysuje się bez
   pętli. (+0,8%)
4. **Niebo nie jest kasowane.** Każda kolumna pamięta, gdzie kończy się czyste niebo. Kasowana jest tylko
   część poniżej, a przemalowywany tylko pas, który się zmienił. (+4,5%)
5. **Rzutowanie bez wywołań.** Rzutowanie 3D liczy dzielenia w miejscu, z szybszą pętlą krawędzi. Ten krok
   zrobił agent Fable. (+4,6%)

Szczegółowy opis techniczny z adresami jest w `TECHNICAL_NOTES.md` (po angielsku).

## Przebudowa i dalsza praca

W paczce jest wszystko, żeby zbudować up38 z v10.1 i pracować dalej: wszystkie źródła asemblera, generatory,
symulator 6502, test równości obrazu bajt w bajt i narzędzia pomiaru odtwarzające protokół nosty3. Najlepiej
zacząć od `TECHNICAL_NOTES.md`, sekcje 2 i 5.

Testowane w Altirrze (emulacja). Na fizycznym sprzęcie przez nas nietestowane.
