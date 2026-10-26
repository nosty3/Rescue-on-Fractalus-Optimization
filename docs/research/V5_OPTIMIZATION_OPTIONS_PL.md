Dokument badawczy zachowany historycznie. Dawne ścieżki i wyniki dotyczą opisanego eksperymentu; aktualną implementację opisuje docs/OPTIMIZATIONS_PL.md, a wyniki zbiorcze docs/benchmarks/METHOD_PL.md (ścieżki od katalogu głównego repozytorium).

[English](V5_OPTIMIZATION_OPTIONS.md) · [Polski](V5_OPTIMIZATION_OPTIONS_PL.md)

# Ponowny audyt v5 — opcje optymalizacji

Data: 21.10.2026. Zakres: badanie, zestawienie i modele kosztu. Nie zmieniono
kodu gry, nie zbudowano nowego wydania ani prototypowego ROM-u.

Punkt odniesienia: wydane v5, XEGS 128 KiB, SHA-256
`9a6445651455d011008238ab5038e4186badc9e4b7a84a2881b6ab2e02d0d5ef`.
Ostatni zmierzony średni wynik pozostaje **7,367256 FPS**, a nie wyniki modeli poniżej.

## Nowe pomiary

Zebrano od początku profil wywołań i profil instrukcji w czterech scenariuszach:
prosto, prawo, lewo i szybki lot w prawo. Każdy przebieg to 3000 ramek PAL,
106 704 000 taktów maszyny, około 60,17 s. Łącznie osiem przebiegów profilera.
Emulator: 800XL, 64 KiB RAM, PAL, bez przyspieszaczy; wszystkie przebiegi
zakończyły się w trybie lotu. Nie mierzono nowego FPS zmodyfikowanej gry.

Ponadto prześledzono instrukcje v5 na 58 zachowanych wejściach renderera,
obejmujących różne kierunki i poziomy. Obserwacja nie zmieniała wykonywanego kodu.
Stare wejścia renderera nie zastępują nowych testów całej rozgrywki.

| Obszar | Średni udział czasu maszyny, koszt własny |
|---|---:|
| Podział i rasteryzacja profilu gór, wejście `$982A`, bank 5 | 33,56% |
| Dzielenie `$8224` | 9,55% |
| Wypełnianie `$9308`, bank 9 | 9,19% |
| Pozostały kod pipeline’u `$87D3` | 6,83% |
| Przygotowanie geometrii `$8309` | 6,49% |
| Przycinanie odcinków `$9627` | 5,17% |
| Projekcja `$85D4`, bez wywołań dzielenia | 5,17% |
| Czyszczenie `$9214` | 4,76% |
| Interpolacja logiki lotu w RAM `$7EEB` | 2,03% |
| Logika lotu `$7310`, bez potomków | 1,71% |
| Główna procedura dźwięku `$B91C`, bez potomków | 1,54% |

Całe VBI z potomkami zajmuje około 11,82%; cały dźwięk około 3,38%.
Te udziały zawierają pozycje z tabeli i **nie wolno ich dodawać**.
Profiler przypisuje instrukcjom również opóźnienia maszyny, w tym DMA.
Adresy bankowane w surowych profilach mają inną reprezentację niż CPU;
np. `$8002B82A` odpowiada wejściu CPU `$982A` w banku 2, które przełącza bank 5.
Koszt pozostaje przypisany temu wejściu mimo przełączenia banku przez JMP.

## Lista opcji i kolejność prób

Zyski poniżej są przyrostami względem 7,367256 FPS. To warunkowe modele,
nie zmierzone wyniki i nie przedziały ufności. Nieudana integracja może dać
zerowy zysk lub regresję. Szczegółowe budżety zapisano w `estimates.json`.

| Priorytet | Pomysł | Wstępny przyrost FPS | Pamięć i ocena |
|---|---|---:|---|
| 1 | Pominąć normalizację dzielenia, jeśli jej stan pomocniczy jest martwy | **+0,10–0,15** | Bez dodatkowego banku. Najmocniejszy model cykli; pozostaje dowód użycia stanu poza rendererem. |
| 2 | Specjalne ścieżki podziału dla szerokości 4 i 5 | **+0,05–0,15** | Szacunkowo 1–3 KiB kodu; potrzebny dobry podział miejsca między głębokościami. Nie przełączać banku dla każdego liścia. |
| 3 | Zamienić interpretowanie stałych tablic kierunku na wygenerowany kod 45 punktów | **+0,03–0,09** | Około 16–32 KiB, 2–4 banki; wybór banku raz na całą procedurę. Budżet, jeszcze bez generatora. |
| 4 | Dokładna interpolacja `$7EEB` przy użyciu tablicy 4 KiB | **+0,03–0,08** | Jeden bank na tablicę i helper; możliwy mały fragment samomodyfikujący w istniejącym kodzie RAM. Arytmetyka sprawdzona, koszt implementacji szacowany. |
| 5 | Poprawić ułożenie gorących skoków i tablic względem granic stron | **+0,007–0,028** | Wyrównania i relokacja, zwykle bez nowego banku. Dane o stratach są zmierzone. |
| 6 | Użyć tej samej tablicy do mnożenia RAM `$7CD6` | **+0,006–0,021** | Dodatkowy helper, wspólna tablica z opcją 4. Stan końcowy i wczesne wyjścia wymagają osobnego dowodu. |
| 7 | Dalsze uproszczenie pętli 14 kanałów dźwięku | **+0,006–0,022** | Mała zmiana kodu; szacowane 2–5 cykli mniej na wpis. Mniejszy priorytet niż góry i dzielenie. |
| 8 | Rozszerzyć specjalizację wypełniania na pierwszy wiersz 33–48 | **+0,004–0,014** | Dodatkowy kod, opłacalne tylko bez nowego przełączania banku dla każdej kolumny. |

Nie sumuję widełek: zmieniają się częstości wywołań, terminy VBI, układ kodu
i konkurencja o miejsce w bankach. Opcje 4 i 6 współdzielą zasób i część kosztów.

## Uzasadnienie najważniejszych pozycji

### 1. Dzielenie bez normalizacji

Obecny kod skaluje licznik i mianownik wspólną potęgą dwójki, aż bit 6
wysokiego bajtu mianownika będzie ustawiony. Następnie wylicza osiem bitów
ilorazu. Dla `0 <= N < D < 32768` algorytm ośmiu kroków może wyliczyć
`floor(256*N/D)` bez tego wstępnego skalowania: przesuwana reszta mieści się
w 16 bitach, a iloraz nie zależy od wspólnego czynnika skali.

W 2766 rzeczywistych wywołaniach mianownik wynosił 64–15330, normalizacja
wykonywała średnio 2,363 przesunięcia. Model ścieżek instrukcji uwzględnia
także zmianę częstości odejmowań po usunięciu normalizacji. Wynik:
13–164 zaoszczędzonych cykli, średnio **66,862**, ten sam iloraz we wszystkich
2766 przypadkach. Koszt modelu obecnej procedury zgadzał się z wykonaniem
niezmienionego kodu 6502 dla 163 rozłożonych po zbiorze przypadków.

W nowym profilu są średnio 21 602 wywołania na 3000 ramek PAL. Daje to około
1,44 mln cykli CPU potencjalnej oszczędności w tym okresie.

Kluczowy warunek: `$AE/$AF/$B0/$B1` nie będą miały dotychczasowych
znormalizowanych wartości. Obserwacja nie wykryła ich odczytu przed
nadpisaniem wewnątrz 58 wywołań renderera. Po ostatnim dzieleniu w każdym
wywołaniu ich użycie pozostaje nierozstrzygnięte: trzeba przejść dalszą pętlę
główną, VBI, pozostałe tryby gry i zależności flag, zwłaszcza V. Jeśli stan
jest wymagany, odtwarzanie go może zjeść zysk. To nie jest jeszcze dowód
pełnej równoważności ani gotowa poprawka.

### 2. Krótkie odcinki gór

Obecny renderer ma specjalizację szerokości 3. W śladzie było 2824 wejść
o szerokości 4 i 1704 o szerokości 5. Znana szerokość pozwala ominąć część
testów, obsługi stosu podziałów i powrotów, zachowując tę samą kolejność
zaokrągleń i sprawdzania zasłonięcia. Model zakłada 35–55 cykli oszczędności
brutto na takim wejściu, a odejmuje 5 cykli dodatkowego wyboru ścieżki
od każdego z 11 455 wejść o szerokości większej niż 3.

Bank 5 ma ograniczone miejsce: koniec wygenerowanego kodu to `$966E`,
wejście przełączające leży pod `$982F`. Należy zacząć od najczęstszych
głębokości, współdzielić kod albo ograniczyć rzadsze specjalizacje.
Dodatkowy bank pomaga przechować cały wariant, ale częste przełączanie
przy pojedynczym liściu może skasować oszczędność. Szacowany zakres nie
obejmuje takiego kosztownego projektu.

### 3. Stałe komendy geometrii

`$8309` wybiera jedną z czterech tablic pod `$9A55/$9A82/$9AAF/$9ADC`,
a następnie interpretuje jej 45 wpisów od `$8360`. Dane komend są stałe.
Można wygenerować cztery warianty kodu z wybranymi z góry operacjami i
adresami punktów. Odpada odczyt komendy, część przesuwania/testów jej bitów,
obsługa indeksu pętli i część narzutu adresowania. Obliczenia zależne od
pozycji statku, wysokości i przycinania pozostają wykonywane.

Budżet: 20–45 cykli mniej na punkt, 45 punktów, około 439 wywołań na
przebieg; odjęto 40 cykli bankowania na wywołanie. Rozmiar 16–32 KiB
jest szacunkiem do potwierdzenia generatorem, nie gotową alokacją.

### 4. Tablicowa interpolacja i RAM

Kod RAM `$7EEB–$7FC1` wykonuje trzy interpolacje po osiem kroków.
Zachowanie jego zaokrągleń jest ważniejsze niż zastąpienie go zwykłym
wzorem na interpolację liniową. Wyprowadzono tabelę wkładu czterech bitów:
`T[maska_4bit][wartość_8bit]`, czyli **16*256 = 4096 bajtów**.
Pełny wkład ośmiu bitów można złożyć z dwóch odczytów: dla górnej połówki
maski i wartości oraz dolnej połówki maski i wartości przesuniętej o 4.
Dla dwóch końców odcinka używa się maski i jej dopełnienia.

Sprawdzono wszystkie 65 536 tożsamości wkładu i 1000 pełnych losowych
przypadków interpolacji względem oryginalnego kodu 6502: wynik `$62` był
zgodny. Nie dowodzi to jeszcze zgodności wszystkich flag, rejestrów,
pamięci pomocniczej, czasu przerwań ani kosztu przyszłego kodu.

Szacowany budżet to 200–350 cykli oszczędności netto na interpolację,
2250 wywołań na przebieg. Sama procedura zajmuje tylko 2,03% czasu,
więc nawet duże jej przyspieszenie nie da kilku dodatkowych FPS.

## Gdzie samomodyfikacja ma sens

| Miejsce | Możliwe zastosowanie | Warunek opłacalności |
|---|---|---|
| Interpolacja w RAM | Zmiana starszego bajtu operandów odczytu tablicy, zależnego od połówki ułamka | Kilka odczytów na jeden ustawiony operand; właściwy zysk daje tablica, SMC jest opcją dostępu. |
| Większy blok renderera skopiowany do RAM | Stały dla bloku bufor, maska lub adres tablicy w operandach instrukcji | Parametry muszą być użyte wielokrotnie; najpierw znaleźć i potwierdzić miejsce w RAM. |
| Komendy geometrii | Mały wariant aktualizowany raz na większą partię pracy | Zwykle prostsze będą gotowe warianty ROM; łatki wykonywane co punkt zjedzą oszczędność. |

Nie warto automatycznie zamieniać każdego `LDA ($80),Y` na samomodyfikujące
`LDA abs,Y`. Odczyt zyskuje zwykle 1 cykl, zapis kolejny 1, a samo zapisanie
nowego 16-bitowego operandu kosztuje co najmniej dwa `STA abs`, czyli
8 cykli, jeszcze bez przygotowania adresu. Dwa różne operandy mogą kosztować
16 cykli. W rasteryzatorze adres często zmienia się po pojedynczym pikselu.

Analogicznie podstawianie mianownika do 24 operandów immediate rozwiniętego
dzielenia kosztowałoby 96 cykli samych zapisów. Zysk z szybszych odczytów
jest zbyt mały dla jednego dzielenia. W zbiorze tylko 949 z 2766 mianowników
było równych poprzedniemu; to nie uzasadnia takiego projektu.

SMC wymaga RAM: sam ROM cartridge'a nie stanie się zapisywalny po dodaniu
banku. Trzeba uwzględnić inicjalizację kodu po zimnym starcie i START,
przełączanie banków danych oraz współdzielenie z przerwaniami. `SEI` nie
blokuje NMI/VBI. Wskazany jest prywatny fragment kodu dla danego kontekstu
lub dowód, że przerwanie nie wykona częściowo zmienionych instrukcji.
Nie potwierdzono jeszcze nowego wolnego obszaru RAM do relokacji renderera.

## Mniejsze opcje i ograniczenia

- W śladzie wystąpiło 55 116 dodatkowych cykli z przekroczenia stron,
  w tym 17 700 dla skoków. Usunięcie wszystkich byłoby nierealistycznym
  pułapem; model układu kodu zakłada usunięcie 25–65% bez regresji innych ścieżek.
- Pierwszy wiersz większy niż 32 wystąpił w 501 z 2436 kolumn (20,57%).
  W v5 zapis nieba jest już rozwinięty także dla tych kolumn. Nie należy
  ponownie doliczać całego kosztu rozwijania nieba; pozostaje mały zysk
  z pierwszej iteracji i dalszego wypełniania.
- 5019 z 13 893 zapisów pikseli trafiało pod ten sam adres co poprzedni
  zapis. Łączenie masek lub pamiętanie bieżącego bajtu jest opcją rezerwową,
  orientacyjnie **0–0,03 FPS** po koszcie wykrywania. Trzeba zachować kolejność
  aktualizacji horyzontu i widoczności; sam odsetek trafień nie dowodzi zysku.
- Tablice przejść dla wypełniania mogą połączyć AND/ORA i obliczenia masek.
  Wystąpiło jednak 15 różnych stanów maski, a wiele kolumn kończy się szybko.
  Koszt wyboru stanu, układu tablic i bankowania nie jest jeszcze policzony.
  Bez tego brak wiarygodnego szacunku FPS; niższy priorytet niż tabela główna.
- Czyszczenie w v4/v5 ma już 1880 bezpośrednich zapisów. Dalsze rozwijanie
  instrukcji nie przyniesie istotnego zysku. Usuwanie zapisów wymaga zmiany
  organizacji bufora i dowodu, że stara zawartość nigdy nie zostanie odczytana.
- Duża tablica ilorazów nie pasuje wprost do 16-bitowych argumentów;
  tablice odwrotności wymagają mnożenia i dokładnej korekcji wyniku. Najpierw
  warto sprawdzić znacznie tańsze pominięcie normalizacji.
- Nie traktować WSYNC ani NOP w DLI jako zwykłych zbędnych instrukcji.
  Część kosztu utrzymuje właściwy moment zmian kolorów i rejestrów obrazu.
- Nie zmniejszać częstości logiki ani dźwięku w ramach tych propozycji:
  to zmiana zachowania gry, a nie równoważna optymalizacja kodu.

## Dostępne banki i sposób wykorzystania

W obrazie v5 **banki 10, 11, 12, 13 i 14 są w całości puste: 40 KiB**.
Nie ma obecnie potrzeby powiększania cartridge'a ponad 128 KiB. To przestrzeń
ROM, nie dodatkowy RAM Atari; badanie dotyczy nadal maszyny z 64 KiB RAM.
Bank 15 jest stały. Bank 7 zawiera kopię dawnego banku stałego; nie zaliczono
go do wolnego miejsca bez audytu wszystkich wyborów banków.

Rozsądny roboczy podział: jeden bank na arytmetykę tablicową, 2–4 banki
na warianty geometrii, pozostałe miejsce na warianty rasteryzacji.
Pełne maksymalne warianty wszystkich pomysłów mogą się jednocześnie nie zmieścić.
Przełączać bank przy wejściu do całej procedury, nie przy każdym pikselu.
Osłona VBI v5 rozpoznaje znaczniki banków poniżej 10. Użycie banków 10–14
wymaga rozszerzenia tej osłony i testów START/VBI/DLI; samo wgranie kodu
do pustego banku nie wystarczy.

## Metoda szacowania i materiały

Dla kosztów CPU stosowano `F_nowe = F_v5 / (1 - alfa * oszczędzone_cykle / T)`,
gdzie `T=106704000`, a `alfa=1..1,5` jest jawną analizą wrażliwości na DMA
i miejsce wykonywania kodu, nie zmierzonym współczynnikiem ani prawdopodobieństwem.
VBI jest cykliczne, prezentacje są zsynchronizowane z PAL, a szybsza gra
może oglądać nieco inne sceny. Dlatego rzeczywisty FPS wymaga późniejszego
pomiaru kompletnego wariantu, także w scenariuszach, które mogą zwolnić.

Dowody i skrypty:

- `results/research_v5/summary.json`: cztery profile, koszty i częstości.
- `results/research_v5/arithmetic-models.json`: sprawdzone modele arytmetyki.
- `results/research_v5/divider-liveness.json`: zakres obserwacji stanu pomocniczego.
- `results/research_v5/estimates.json`: jawne budżety oraz przeliczenie na FPS.
- `scripts/research_v5_*.py`: profilowanie, odczyt kodu, ślad, arytmetyka i obliczenia.

Surowe profile i lokalny odczyt RAM służą analizie na obecnym komputerze.
Kopia repozytorium zawiera raport, skrypty i zwięzłe wyniki, bez dumpu RAM.
Skrypty śladu wymagają dawnych lokalnych wejść renderera, których zgodnie
z przyjętym zakresem kopii nie publikuje się. Po utracie tych plików należy
zebrać nowe wejścia; nie da się obiecać odtworzenia identycznych śladów.
