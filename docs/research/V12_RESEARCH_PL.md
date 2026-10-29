Historyczne badanie kandydata włączonego do v12. Pełny test: ../benchmarks/V12_REPORT_PL.md.

# Dalsza optymalizacja w 128 KB — działający kandydat

2026-10-29. Baza porównawcza: v11 z zachowanym samym `$AA` (SHA-256 `7bd31c022afd3c3e81e161106b66851c0d12c26a04864c8569d510b99eb917d3`). Kandydat: `4959a82ab36528a0448a40e6178fdb72d321e5d1e23c258036f5e22e51cfa20e`. Cartridge pozostaje 128 KB, bez rozszerzonego RAM, zmiany grafiki, odległości rysowania ani celowego tempa gry. Nie jest to nowe numerowane wydanie; oficjalne v11 i XEX pozostają niezmienione.

## Przyjęte zmiany

1. **Pierwszy punkt skanu zasłaniania sprawdzany wcześniej.** Jeżeli już on wyklucza pominięcie poddrzewa, wracamy do dokładnego podziału przed przygotowaniem licznika grup. Nie zmieniono konserwatywnej granicy wysokości ani warunku zasłonięcia.
2. **Tablica liczby grup czterech kolumn.** Mała tablica w dotychczasowym wypełnieniu banku 5 zastępuje `TYA/CLC/ADC/LSR/LSR/TAY`. Zachowuje dokładną dotychczasową arytmetykę 8-bitową, również zawijanie dla szerokości 253–255. Położenie `$9600` eliminuje karę odczytu przy przekraczaniu strony.
3. **Także wejściowy test całego odcinka trzyma próg w A.** Zamiast czterech par LDA/CMP są cztery CMP z pamięcią i INX zachowujące A. Osobne wyjście dla `Hmax=0` zabezpiecza odejmowanie jedynki; nie stosujemy tej transformacji bezwarunkowo.
4. **Pełniejsze usunięcie obsługi głębokości w Y.** W wyspecjalizowanych d0–d4 Y służy już do operacji bitmapy, bez zbędnych INY/DEY/LDY natychmiastowych i odtwarzania go po nieudanym cull. Przy wejściu do ogólnego kodu przywracamy **Y=5**. To ważna różnica względem generatora ilmenita dla starszego kodu z d0–d7; wpisanie tam Y=8 byłoby błędem. Rzeczywisty wywołujący wczytuje Y z `$272E` po powrocie renderera.
5. **Mała poprawka geometrii ilmenita.** Grupowanie klasyfikacji punktów 33–43, klasyfikacja punktu 44 inline i krótsze ustawienie pożyczki przez CMP. Kolejność obliczania współrzędnych i próbkowania mapy pozostaje zachowana. Ten pomysł oraz szersze usuwanie Y pochodzą z paczki ilmenita; bazowy renderer i cache są pracą wcześniejszych etapów nosty/ChatGPT, Solo/Opus i późniejszych poprawek v11.

Źródła MADS: `candidate.asm` (bank 5), `sky_b9.asm` (wcześniejszy `$AA`, bank 9), `geometry_bank10.asm`–`geometry_bank13.asm`. Nie dodano zmiennych RAM ani nowych banków. Znaczniki banków i synchronizacja kasowania bufora pozostają zgodne z v11.

## Co nie weszło

Próg testów zasłaniania dobierano na 40 scenach dla pięciu głębokości, po kilka wartości i dwa przebiegi doboru. Większość pominięć pogarszała wynik. Najlepsza stara konfiguracja dawała zaledwie około 20 cykli na scenę; do kandydata przyjęto ulepszenie samej procedury, bez dostrajania progów do tych map.

Dwie wersje łączenia dwóch widocznych pikseli o tej samej wysokości w jednym bajcie były zgodne obrazowo, lecz **zwiększały koszt** względem odpowiadającego im kodu bez łączenia: około 413 i 346 cykli na scenę. Koszt rozpoznawania oraz zachowania cache/flag zjadł korzyść. Nie są w kandydacie. Nie wyklucza to innego przyszłego sposobu grupowania zapisów.

## Koszt kodu

Poniżej 80 tych samych scen, dodatnia oszczędność względem samego `$AA`. Poszczególne wiersze są kompletnymi wariantami, nie przyrostami do sumowania:

| Wariant | Średnio mniej cykli/scenę | Redukcja |
|---|---:|---:|
| `cull_early` | 378.65 | 0.3457% |
| `cull_groups` | 531.01 | 0.4848% |
| `cull_root` | 926.70 | 0.8461% |
| `depth` | 2099.90 | 1.9172% |
| `pair_12` | 513.91 | 0.4692% |
| `pairdepth_12` | 1753.53 | 1.6009% |

Końcowy kandydat: **320 scen, 2108.95 cyklu mniej na badany odcinek renderowania, 1.9291% oszczędności**. Na 40 osobnych scenach k=4,12,… wynik wynosi 1.8815%; nie były używane przy doborze progów. Wszystkie 320 porównań mają zgodny obraz, horyzont, aktywny cache, żywy stan i końcowe flagi CPU.

**Zakres ma znaczenie:** zapisane okno `$A331/$A36F` obejmuje kasowanie, projekcję/teren i fill, a przygotowanie geometrii jest wcześniej. Geometrię sprawdzono oddzielnie w 320 przypadkach: identyczny aktywny RAM i rejestry/flag CPU, średnio **176.69375 cyklu mniej**. Nie przedstawiamy tych liczb jako procentu przyspieszenia całej gry.

## Ograniczony pilot FPS

64 zimne starty: 2 ROM-y × PAL/NTSC × lot prosto/nurkowanie × 8 wybranych z góry startów. Okna nominalnie 15 s, domykane do całego odstępu prezentacji `$B516`; wszystkie 64 loty ukończyły okno, bez zakończenia gry. Rozgrzewka 170 ramek wideo, impuls joysticka w górę 1 s co 4 s, cztery niezależne emulatory i szybki transport poleceń jak we wcześniejszej metodyce. Nie przenoszono stanów między ROM-ami; początkowe mapy dla odpowiadających sobie startów były zgodne.

Średnia 50/50 z obu scenariuszy; procent to iloraz średnich, nie średnia procentów:

| System | Baza z $AA FPS | Kandydat FPS | Zmiana FPS | Wzrost |
|---|---:|---:|---:|---:|
| PAL | 8.7814 | 8.9573 | +0.1759 | +2.00% |
| NTSC | 7.5275 | 7.6312 | +0.1036 | +1.38% |

Osobne scenariusze:

| System | Scenariusz | Baza FPS | Kandydat FPS | Wzrost |
|---|---|---:|---:|---:|
| PAL | straight | 8.9700 | 9.1482 | +1.99% |
| PAL | steering | 8.5929 | 8.7664 | +2.02% |
| NTSC | straight | 7.9729 | 8.1178 | +1.82% |
| NTSC | steering | 7.0821 | 7.1445 | +0.88% |

Wynik rokuje dobrze, ale **to pilot z ośmioma startami i krótszym lotem, a nie pełna seria 155 lotów po 60 s**. Nie zastępuje oficjalnych średnich ani nie ustala nowego procentu względem oryginału. `pilot-results.json` zawiera także orientacyjne 95% przedziały bootstrap, z resamplingiem całych par startów i zachowaniem obu scenariuszy. Przy ośmiu klastrach ich precyzja jest ograniczona. Próg 0,05 FPS traktujemy obecnie orientacyjnie, zgodnie z decyzją użytkownika.

## Walidacja i odtworzenie

- 4000 losowych odcinków: clipping, wysokości/nasiona, istniejąca bitmapa i cache HD 108–152; zgodne bitmapy, cały horyzont, cache oraz X/SP. A/Y/flag na pojedynczym wyjściu nie wymagamy identycznych, ponieważ rzeczywisty wywołujący ich nie konsumuje w tej postaci.
- 332 jawne przypadki `Hmax=0`, szerokości 1/2 w wewnętrznych pozycjach: zgodne wyniki.
- 160 scen z natywnej historii kandydata, PAL/NTSC, losowe kierunki i strzelanie: zgodne renderowanie, żywy stan i wszystkie końcowe flagi. Sześć cykli Esc/pauza/wznowienie: poprawne.
- Brak pełnego testu wszystkich poziomów, sprzętu i akceleratorów. Odpowiednik XEX i jego osobne testy opisuje [XEX_PL.md](XEX_PL.md). Nie zmieniono procedury oczekiwania na dostęp do bufora.

Budowanie: `python experiments/compact_128/build.py`. Wymaga opublikowanego lokalnego ROM v11, sześciu lokalnych źródeł ASM oraz MADS z projektu; nie potrzebuje paczki ilmenita ani jej generatorów. Wynik sprawdzany SHA-256. Do uruchomienia służy jedyny CAR/ROM w głównym katalogu eksperymentu: `Fractalus - compact candidate 128KB experiment`.

Badania: `research.py` odtwarza próby skanów, usuwania Y i łączenia par; `validate_candidate.py fuzz`, `zero`, `geometry`, `native` odtwarzają walidację; `native_pilot.py` wykonuje pilot albo wczytuje zgodne zapisane wyniki. Dla nowego badania trzeba użyć osobnego katalogu wyników; istniejący cache nie jest nowym pomiarem. `write_report.py` odtwarza raporty. Robocze źródła, binaria i odrzucone obrazy są w `work/`.

Następny odrębny kierunek pozostaje ten sam: dokładne dzielenie w projekcji, z rygorystycznym bilansem integracji. W tym etapie go nie zmieniano.
