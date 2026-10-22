Dokument badawczy zachowany historycznie. Dawne ścieżki i wyniki dotyczą opisanego eksperymentu; aktualną implementację opisuje docs/OPTYMALIZACJE_PL.md, a wyniki zbiorcze docs/benchmarks/METODA_PL.md (ścieżki od katalogu głównego repozytorium).

# Rozkład FPS i propozycja wiarygodnej procedury NTSC

Analiza dotyczy istniejących 80 prób: dwóch serii po 20 niezależnych startów każdej wersji. Nie wykonano nowych lotów. Wszystkie wyniki zachowano, również skrajne. Kod analizy: `scripts/analyze_ntsc_distribution.py`; szczegółowe statystyki: `distribution_analysis.json`.

## Wyniki opisowe

| Wersja / seria | Średnia FPS | Mediana FPS | Odchylenie standardowe | Środkowe 50% wyników (Q1–Q3) |
|---|---:|---:|---:|---:|
| Oryginał / 1 | 5,7764 | 5,6786 | 0,2776 | 5,5866–5,8709 |
| Oryginał / 2 | 5,7708 | 5,7401 | 0,2324 | 5,6115–5,8477 |
| v9 / 1 | 6,7344 | 6,7355 | 0,1935 | 6,6047–6,8649 |
| v9 / 2 | 7,0054 | 7,0281 | 0,3153 | 6,7809–7,2033 |

Oryginał ma w obu próbkach prawy ogon: kilka wysokich FPS podnosi średnią ponad medianę. Skośność próbkowa wynosi 1,12 i 1,43. Próbki v9 są w przybliżeniu symetryczne (skośność 0,05 i 0,01), lecz mają inne położenie i rozrzut. Przy n=20 nie można wiarygodnie ustalić dokładnej rodziny rozkładu. Brak odrzucenia normalności v9 w teście Shapiro–Wilka nie dowodzi normalności populacji. Próbki oryginału wykazują odchylenia od normalności (p=0,048 i 0,010), ale testy te są tylko diagnostyczne.

Wykres `ROZKLAD_FPS_NTSC_PL.png` pokazuje dystrybuanty empiryczne bez dobierania przedziałów histogramu. Każdy punkt reprezentuje jeden lot. v9 ma przesuniętą także medianę, a nie tylko średnią. Reguła 1,5 IQR nie oznacza żadnego wyniku v9 jako odstającego; oznacza 1 i 2 wyniki oryginału. Nie jest to podstawa do ich usunięcia: łatwiejszy teren jest poprawnym wynikiem testu.

## Porównanie serii i ograniczenia wnioskowania

- Oryginał: różnica średnich -0,0056 FPS. Test Welcha p=0,945; test permutacyjny p=0,946. Brak wykrytej różnicy nie jest dowodem ścisłej równoważności.
- v9: różnica średnich +0,2710 FPS. Test Welcha p=0,00256, orientacyjny przedział ufności 95% różnicy +0,1025 do +0,4396 FPS. Test permutacyjny (100 000 losowań) p=0,00232; test Manna–Whitneya p=0,00512. Ten ostatni bada różnicę rozkładów/rang, nie samych średnich.
- Zysk serii 1: +16,58%, orientacyjny przedział bootstrap 95% +13,79% do +19,33%.
- Zysk serii 2: +21,39%, orientacyjny przedział bootstrap 95% +18,24% do +24,48%.

Są to analizy eksploracyjne, p bez korekty wielokrotnych testów. Testy zakładają niezależność i odpowiednią porównywalność prób; permutacja zakłada wymienność pod hipotezą zerową. p nie jest prawdopodobieństwem błędu emulatora ani hipotezy zerowej. Nie rozstrzygamy, czy przyczyną różnicy była pechowa próbka map, sposób ich losowania, stan emulatora czy inny czynnik. Bootstrap również nie naprawia systematycznego błędu ani niestabilnych warunków.

W serii 2 v9 FPS koreluje z czasem oczekiwania przed START: Spearman rho=0,641, p=0,00234; w serii 1 ten związek się nie powtarza (rho=-0,211, p=0,373). W serii 1 v9 pojawia się wzrost wraz z numerem próby (rho=0,471, p=0,036), którego brak w serii 2. Oryginał serii 2 ma ujemną korelację z oczekiwaniem (rho=-0,483, p=0,031). To wskazówki do audytu inicjalizacji i próbkowania, nie ustalone prawa. Wylosowanie różnych tablic nie gwarantuje ich niezależności ani reprezentatywnego rozkładu.

## Rekomendacja: najpierw kontrola procedury, następnie większa próbka

### 1. Audyt powtarzalności technicznej

Przed setkami pomiarów przeprowadzić mały, osobno oznaczony test odtwarzania identycznego scenariusza. Użyć nowego procesu emulatora dla każdego uruchomienia, identycznej konfiguracji i kontrolowanego momentu START. Każda wersja ma uruchamiać własny ROM i własną inicjalizację. Zapisać konfigurację, hashe obrazu i danych świata, poziom, pozycję, kierunek, prędkość oraz znaczniki ukończonych obrazów.

Sprawdzić, czy powtórzenie w tej samej wersji rzeczywiście daje ten sam świat i przebieg. Gdy świat się różni, wyjaśnić źródła losowości/ziarna przed uznaniem testu za deterministyczny. Gdy świat i warunki są identyczne, ale pomiary nie są, zbadać zegar, synchronizację i licznik obrazów. Dodatkowo porównać świeży proces z dotychczasowym wielokrotnym BOOT w jednym procesie. Zapisów żadnej wersji nie przenosić do drugiej.

### 2. Pomiar normalnych uruchomień bez modyfikacji gry

- Z góry ustalić scenariusz: NTSC, początkowy poziom, jednakowa rozgrzewka i jeden lot prosto. Wniosek dotyczy tego scenariusza; ogólna wydajność gry wymaga również innych reprezentatywnych scenariuszy.
- Zaplanować loty 60-sekundowe jako rozsądny punkt wyjścia, ale najpierw pilotem sprawdzić, czy taki czas zmniejsza rozrzut i nie wprowadza końca gry albo innych zmian scenariusza. Nie zakładać, że 4 razy dłuższy lot daje 4 niezależne próbki. Zachować znaczniki pośrednie 15/30/60 s jako wyniki zależne tego samego lotu.
- Nowy proces emulatora i natywny start gry dla każdej próby. Losowanie momentu START z wcześniej ustalonego zakresu, po potwierdzeniu gotowości menu. Szerszy zakres nie jest gwarancją jednostajnego losowania map; trzeba kontrolować rozkład danych świata.
- Małe zrównoważone bloki czasowe, np. po 5 prób oryginału i 5 v9, z losową kolejnością wewnątrz bloku. Zachować blok w analizie. To ogranicza pomylenie wersji z czasem/warunkami uruchamiania, ale nie wyrównuje map.
- Zachować wszystkie poprawne próby. Z góry ustalić kryteria błędu technicznego; kolizji lub końca gry nie usuwać po fakcie tylko dlatego, że zmieniają średnią. Ich obsługę trzeba określić w scenariuszu.
- Jednostką statystyczną jest osobny lot, nie każda klatka ani każde 15 s tego samego lotu.
- Dla każdego lotu liczyć liczbę ukończonych obrazów / czas. Następnie raportować średnią FPS lotów i jej przedział ufności oraz zysk G=100*(średnia_v9/średnia_oryginał-1) z własnym przedziałem. Dodatkowo mediana i rozrzut; bez usuwania skrajnych poprawnych lotów.
- Przedziały bootstrap obliczać przez losowanie całych niezależnych lotów, a przy grupowaniu przez wspólne warunki losować odpowiednie całe bloki. Nie losować pojedynczych klatek. Nadal trzeba sprawdzić stabilność między blokami.

### 3. Dokładność i wielkość próbki

Wybrać z góry praktyczny cel, np. przedział ufności 95% dla procentowego zysku o połowie szerokości nie większej niż 1 punkt procentowy (wynik np. +19% ±1 p.p.). To inne wymaganie niż ±1% względnie dla średniego FPS jednej wersji.

Warunkowe oszacowanie na podstawie obecnego rozrzutu 15-sekundowych prób, przy stabilnych niezależnych uruchomieniach:

| Cel | Przybliżona liczba lotów na wersję |
|---|---:|
| Średni FPS każdej wersji: ±1% względnie, 95% | 70–74 |
| Procentowy zysk: ±2 punkty procentowe, 95% | 51 |
| Procentowy zysk: ±1 punkt procentowy, 95% | 203 |

To przybliżenie normalne do planowania, a nie gwarancja. Dla ilorazu średnich zastosowano propagację wariancji: n ≈ (1,96*R/h)^2*(CV_original^2+CV_v9^2), gdzie R jest ilorazem średnich, h żądaną połową szerokości dla R (0,01 odpowiada 1 p.p. zysku), a CV to odchylenie standardowe / średnia. Obserwowane przesunięcie v9 ogranicza zasadność założenia stabilności. Liczby należy przeliczyć po audycie i pilocie 60 s.

Praktyczny plan: osobny pilot 20 lotów na wersję po 60 s, sprawdzenie rozrzutu i stabilności bloków, następnie ustalenie stałej liczby prób głównego testu przed jego rozpoczęciem. Danych pilota nie dodawać automatycznie do testu potwierdzającego. Nie kończyć zbierania tylko dlatego, że aktualny wynik wygląda dobrze; przy adaptacyjnym zatrzymywaniu potrzebna jest właściwa metoda sekwencyjna. Sam brak istotnej różnicy między dwiema seriami nie stanowi kryterium zgodności — określić dopuszczalną różnicę i ocenić jej przedział.

## Opcja do pomiaru samych optymalizacji: pary tych samych światów

Najlepsza kontrola zmienności terenu to niezależna inicjalizacja obu ROM-ów z jednakowymi, kontrolowanymi danymi świata i warunkami lotu. Nie oznacza to przenoszenia całego stanu pamięci, stosu czy rejestrów z oryginału do v9. Można rozważyć kontrolę wejścia generatora losowego na etapie generowania świata lub przekazanie wyłącznie zidentyfikowanych danych świata po natywnej inicjalizacji. Wymaga to osobnego dowodu zgodności wszystkich zależnych danych, nie samej tablicy $0900.

Przy tym samym świecie obie wersje powinny wykonać zdefiniowane porównywalne zadanie. Ponieważ szybsza pętla może wpływać na tempo symulacji, należy sprawdzić trasę i stan świata w toku testu, a nie zakładać zgodności na podstawie samego początku. Test ustalonej liczby odpowiadających sobie aktualizacji lub klatek na tej samej trasie mierzy przyspieszenie obliczeń; test 60 s gry mierzy wrażenia użytkownika. To odrębne pytania.

Dla zweryfikowanych par analizować różnice i iloraz średnich z bootstrapem całych par. Parowanie zmniejszy niepewność tylko w takim stopniu, w jakim trudność tych samych światów wpływa podobnie na obie wersje; nie da się teraz obiecać konkretnej redukcji liczby prób. Taki benchmark uzupełnia test normalnych startów, ale go nie zastępuje.

## Źródła metodologiczne

- NIST, projektowanie blokowe i losowanie kolejności: https://www.itl.nist.gov/div898/handbook/pri/section3/pri332.htm
- NIST, przedziały ufności średniej i zależność dokładności od rozrzutu oraz liczby obserwacji: https://www.itl.nist.gov/div898/handbook/eda/section3/eda352.htm

Wniosek: nie mamy podstaw, by sprowadzić problem do zbyt małej liczby prób albo samych wartości skrajnych. Trzeba najpierw wyjaśnić stabilność inicjalizacji/próbkowania, a później mierzyć według z góry zadanej dokładności. Większa próbka zmniejsza błąd losowy, lecz nie usuwa systematycznych zmian warunków.
