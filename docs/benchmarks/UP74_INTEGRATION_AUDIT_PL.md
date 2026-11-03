# Audyt up74 i możliwości integracji

[English](UP74_INTEGRATION_AUDIT.md) · [Polski](UP74_INTEGRATION_AUDIT_PL.md)

Analiza lokalna, 2026-11-03. Bez commitów, publikacji i zmian w wydaniach v11–v13. Paczka wejściowa `opus_i_fable/fractalus-up74` pozostała nienaruszona. Robocza kopia, testy i warianty znajdują się w tym katalogu.

## Wniosek

**Najlepszą bazą dalszej pracy jest up74, pozostające przy 128 KB.** To rzeczywista, szeroka optymalizacja v11. Nie należy nakładać na nie całych banków v12/v13: zastąpiłyby szybsze implementacje Solo starszymi. Nasza dotychczasowa geometria przyrostowa także nie daje przewagi nad nową geometrią Solo.

Gotowe drzewa ilmenita pozostają pomysłem na osobny wariant, ale **sprawdzone sposoby ich połączenia z up74 pogarszają koszt renderowania**. Większa pojemność nie oznacza tu automatycznie większej szybkości. Ewentualna dalsza praca wymaga generatora wykorzystującego nowe algorytmy Solo, a nie przeniesienia obecnego v13.

Wynik dla niezależnego skrótu `$AA`: patrz końcowe zestawienie poniżej. Drobne usunięcie pozostałych operacji Y jest możliwe, ale wymaga zachowania adresów gorącego kodu i daje około 11–13 cykli na obraz, nie duży skok FPS.

## Sprawdzenie deklarowanej wydajności

| System, średnia 50/50 | Oryginał | v11 | up74 | up74 / oryginał | up74 / v11 |
|---|---:|---:|---:|---:|---:|
| PAL | 6,2717 FPS | 8,7829 FPS | **10,9172 FPS** | **+74,07%** | **+24,30%** |
| NTSC | 5,5915 FPS | 8,0031 FPS | **9,8961 FPS** | **+76,98%** | **+23,65%** |

To średnie przeliczone z 620 dostarczonych obserwacji up74: 155 lotów na każdy system i scenariusz. Nie przedstawiam ich jako 620 nowych pomiarów wykonanych w tym audycie. Niezależnie uruchomiłem **50 lotów od zimnego startu**: z góry wybrane pozycje rozłożone po każdej serii, dodatkowo obejmujące naturalne zakończenia lotu. Wszystkie 50 odtworzyło dokładnie FPS, liczbę interwałów prezentacji i hash wejściowego RAM-u z paczki. To silne potwierdzenie odtwarzalności jej wyników.

Szczegóły up74: PAL prosto 11,32771777; PAL nurkowanie 10,50674380; NTSC prosto 10,36047279; NTSC nurkowanie 9,43175131 FPS. W dokumentacji Solo NTSC 50/50 zapisano 9,8962; przeliczenie bezpośrednio z JSON-ów daje 9,89611205, czyli **9,8961** po zaokrągleniu do czterech miejsc. Różnica jest wyłącznie drobną rozbieżnością tabeli z danymi.

Warunki: Atari 800XL/64 KB, bez akceleratora, świeży proces i zimny start każdego lotu, historyczne `menu_frames`, 170 ramek rozgrzewki, do 60 sekund czasu Atari. Liczenie prezentacji przy `$B516`, czas z zegara emulatora. Nurkowanie: 1 s joystick w górę / 3 s neutralnie. Naturalne końce zachowane; brak odrzucania skrajności. Średnia 50/50 = połowa średniej FPS każdego scenariusza, a procent = iloraz średnich minus jeden.

Szybsze VBI działa już w menu i zmienia moment odczytu POKEY RANDOM. Ten sam czas naciśnięcia START nie zapewnia tej samej planety między v11 a up74. Porównanie z oryginałem/v11 jest więc porównaniem serii niezależnych, nie identycznych tras. Nie przenosiłem stanów między ROM-ami w pomiarach FPS.

## Co rzeczywiście zmienił Solo

| Obszar | Nowa implementacja | Relacja do naszych zmian |
|---|---|---|
| Rasteryzacja gór, bank 5 | Ścisłe ograniczenie wysokości poddrzewa Ex(w), połączone ścieżki podziału i liści, krótsze wyjścia, lepsze użycie Y i ułożenie kodu | Zastępuje dużą część kodu, który przyspieszały v12 i drzewa v13; zysków nie można dodawać |
| Wypełnianie, bank 9 | Propagacja `out = x XOR (Q[x] AND SK)`, `SK' = Z[x] AND SK`; około 32 zamiast 43 cykli na wiersz, specjalizacja również dolnych wierszy | Szybsza ogólna ścieżka; `$AA` można dołączyć osobno, lecz trzeba zmierzyć jego przydatność od nowa |
| Geometria siatki, banki 10–13 | Tablice przesuwania indeksu mapy, wykorzystanie flagi C, połączone kroki na zakrętach spirali, mniej odczytów i zapisów | Szersza optymalizacja niż grupowanie klasyfikacji punktów 33–44 z v12 |
| Przygotowanie i zakończenie geometrii | Tablice i obliczenia w banku 4, szybszy rozwinięty etap końcowy w banku 2 | Obniża koszt pełnego przeliczenia, wobec którego wcześniejszy cache przestaje być korzystny |
| VBI | Mnożenie z tablic banku 7, szybsza interpolacja, kolejka dźwięku ze stanem ważności minimum, szybsze min/max | Nowa, istotna praca; nie jest powtórnym doliczeniem optymalizacji v11 |
| Rzutowanie i pętla krawędzi | Lepszy podział ścieżek dzielenia, usunięcie martwej reszty, tablice skali, mniej pracy sterującej | Należy zachować razem z nową rasteryzacją |
| Oczekiwanie na poprzedni obraz | Część bezpiecznego rzutowania wykonywana przed zakończeniem oczekiwania; bez zapisów do bufora obrazu | Zmniejsza czas tracony na czekanie; same cykle procedur nie opisują całego przyrostu FPS |

Źródła: `package/tools/gen_fill9.py`, `gen_scene.py`, `gen_scene7.py`, `gen_proj.py`, `patches_vbi2.py`, `patches_reorder.py`, `patches_proj.py`, `package/src/v11/raster5.asm`, `package/src/vbi2_snd14.asm` oraz dokumentacja `package/AGENT.md`. Opisy autora potraktowano jako hipotezy do sprawdzenia, nie jako dowód poprawności.

## Warianty integracji i zmierzone koszty

W tabeli są **cykle CPU na identycznych stanach**, bez ANTIC DMA i bez natywnego harmonogramu VBI. To nie są procenty FPS. Dodatni koszt oznacza pogorszenie względem up74.

| Próba | Wynik | Decyzja |
|---|---|---|
| Cały fill v12 zamiast banku 9 Solo | +3537 cykli/obraz, 48 scen | Odrzucić: zachować szybszy fill Solo |
| Banki siatki v12 zamiast 10–13 Solo, reszta Solo | +1272 cykle/przygotowanie sceny, 24 sceny | Odrzucić: zachować siatkę Solo |
| Rasteryzator v12 zamiast banku 5 Solo | +11166 cykli/obraz, 48 scen | Odrzucić; zgodność obrazu nie równoważy straty czasu |
| Same pozostałe `INY`, usunięte bez kompensacji położenia | około +68 cykli/obraz, 384 świeże sceny | Odrzucić tę postać: przesunięcia kodu pogarszają układ stron |
| Te same `INY`, z zachowaniem adresów gorących pętli | około **−11 cykli/obraz**, 384 świeże sceny; −13 w starszym zestawie 48 scen | Mała opcja, nie uzasadnia ogłaszania zauważalnego zysku FPS |
| Drzewa v13 512 KB na up74 | **+1557 cykli/obraz**, 384 świeże sceny | Nie dołączać w obecnej postaci |
| Drzewa v13 1 MB na up74 | **+2027 cykli/obraz**, te same sceny | Nie dołączać; większy zakres wyboru drzew tu szkodzi |
| Drzewa szerokości 40–64 po odrzucaniu ukrytych poddrzew przez Solo, dokładniejsze Ex(w), krótsze wyjścia | **+276 cykli/obraz**, 384 świeże sceny; 27 dodatkowych banków | Lepsza integracja niż prosty port, lecz nadal bez zysku; mieści się w 512 KB, 1 MB wykonuje identyczny kod |

Drzewa sprawdzono też na 3611 rzeczywistych wywołaniach rasteryzatora: bez różnic w obrazie, wysokościach kasowania i przesłanianiu. Niektóre szerokie odcinki przyspieszają, lecz selektor, przełączenia banków i wolniejsze przypadki pochłaniają zysk. Testy całego potoku pozostają celowo ścisłe: zgłaszają różnice w `$0170/$0171` (adres pomocniczego skoku leniwego kasowania), a w wariancie 1 MB również `$B4` (roboczy stan lewego drzewa). Nie przedstawiam tych wariantów jako w pełni zatwierdzonych wydań. Nie mają uzasadnienia wydajnościowego, więc nie wykonywałem dla nich pełnych serii FPS.

**Geometria przyrostowa:** na 320 identycznych stanach stare pełne przeliczenie v13 kosztuje średnio 10031 cykli, istniejący cache 9039, a pełne przeliczenie Solo **7497**. Cache byłby o **1542 cykle wolniejszy**. Nawet optymistyczny model podmieniający jego przygotowanie na szybszy wariant Solo pozostaje o około **395 cykli wolniejszy**, jeszcze bez dodatkowej ceny relokacji i integracji. To model konkretnego istniejącego cache, nie dowód, że każda przyszła geometria przyrostowa jest bezcelowa. Ponadto stary kod cache od `$7F70` nachodzi na nowe mnożenie do `$7F78`, a bank 7 zajmują tablice.

## Próba `$AA` — pełna seria

Wykonano **310 nowych lotów** (155 PAL + 155 NTSC), cztery emulatory, zamrożony mieszany plan v12: 78 lotów prosto i 77 nurkowych na system. Porównanie wykorzystuje dokładnie odpowiadające im obserwacje up74 z paczki. Nie porównuje 155 prób AA z innym podzbiorem up74.

| System | up74, ten sam podzbiór | up74 + AA | Różnica FPS | 95% CI różnicy |
|---|---:|---:|---:|---:|
| PAL | 10.9302 | 10.9590 | +0.0288 | [-0.0166, +0.0743] |
| NTSC | 9.8850 | 9.8652 | -0.0198 | [-0.0723, +0.0331] |

**Nie rekomenduję AA do domyślnego wariantu up74.** Zysk PAL nie jest rozstrzygający, NTSC ma ujemną estymatę, oba przedziały obejmują zero. To nie dowód, że skrót nigdy nie pomaga; nie potwierdzono korzyści w przyjętej metodyce. Bootstrap 10000 replik, z zachowaniem par według menu/trial i osobnych warstw scenariusza, seed 742027. Brak usuwania obserwacji. Naturalne końce: PAL 11/11 (up74/AA), NTSC 10/8.

Inne średnie up74 w tej tabeli i tabeli głównej wynikają z liczebności: tutaj 155 mieszanych lotów na system, tam wszystkie 310 dostarczonych lotów na system. W obu przypadkach stosujemy 50/50, niezależnie od 78/77 liczebności warstw.

309/310 pierwotnych hashów wejścia AA zgadzało się z up74. W PAL trial 54 hash całego RAM-u był raz inny, choć hash mapy był ten sam. Dwa ponowne loty up74 i jeden AA odtworzyły swoje FPS dokładnie, a ponowne odczyty RAM-u obu ROM-ów były identyczne. Oryginalnego pełnego zrzutu tego pojedynczego odczytu nie zapisywano, więc nie ustalono różniących się bajtów; nie przypisuję im wymyślonej przyczyny. Obserwacja pozostała w analizie. Wyniki: `trial54-recheck.log`, `entry-difference-analysis.json`.


## Weryfikacja bezstratności

- Kompilacja MADS daje dokładnie dostarczony ROM; również IPS odtwarza ten sam plik. ROM ma 131072 bajty, CAR 131088 bajtów, typ 14.
- ROM SHA-256: `63baff0da13b5da2678eba44d4b392e7fa3de6df18044233a7eb7b19d796b3c7`.
- Uruchomiony pakiet kontrolny: **14/14 zaliczonych**. Obejmuje potok renderowania, oczekiwanie, rasteryzację, fill, rzutowanie, pętlę krawędzi, VBI i geometrię.
- Nowe nagrania z up74: **384 stany potoku, 384 geometrii i 384 VBI**, lot prosto, nurkowanie, skręty i strzelanie, PAL/NTSC. Bez różnic obrazu/stanu wynikowego w porównaniach v11→up74, z jawnie określonymi martwymi polami i obszarami zmienionego kodu.
- Geometria: około 10209→7503 cykle. Potok renderowania: około 101598→85183 cykle. Są to wyniki nowych stanów, nie FPS.
- VBI: identyczna kolejność i wartości zapisów sprzętowych; około 3741→3285 cykli. Przy porównaniu trzeba wyrównać sam znacznik banku 4 w referencji v11: up74 rzeczywiście wykonuje tam teraz kod, a stare v11 miało `$FF`, oznaczające powrót do banku 2. Pierwsze porównanie bez tej korekty miało zero różnic RAM/sprzętu i sześć oczekiwanych różnic numeru banku. Nie ukryto ich przez ogólne ignorowanie banków.
- Mnożenie: **wszystkie 65536 par**, zero różnic, średnio 136,46→66 cykli.
- Rzutowanie: **10000 losowych przypadków**, zero różnic, w tym 1002 rzadkie ścieżki widoczności.
- Dźwięk: **10000 syntetycznych kolejek**, z przydziałami kanałów, inicjalizacjami efektów, głośnościami 0–15 i unikalnymi głosami. **160568 identycznych zapisów sprzętowych**, zero rozbieżności RAM/przydziału/powrotu; 4725→3757 cykli na tę syntetyczną kolejkę. To nie pomiar przeciętnego VBI ani test odsłuchowy wszystkich sytuacji gry.
- Praca podczas oczekiwania: 96 nowych scen × 4 długości oczekiwania, bez rozbieżności; sprawdzona także ścieżka przerywająca wcześniejsze rzutowanie dla specjalnej widoczności.
- Skrót AA: 384 nowe potoki i 1000 losowych przypadków fillu bez różnic. W tych potokach nie daje oszczędności średnio: około +10 cykli, dlatego osobno wykonano pełne loty.

- Rozszerzony test rasteryzatora: **10000 odcinków, zero rozbieżności**, w tym 1070 brzegowych, 1046 szerokich, 2263 małych, 2263 z leniwym kasowaniem i 1128 z ograniczaniem wysokości. Referencja zawiera rasteryzator v11 w up74, aby kod wywołujący i adresy powrotu były identyczne; nie przenoszono błędnie adresów powrotu pomiędzy różnymi pętlami krawędzi. Różnice roboczych A/Y/P sprawdzono przez wykonanie reszty potoku — wynik pozostał identyczny. Średni koszt odcinka w tym syntetycznym zbiorze: 4464→4001 cykli.
- **8/8 natywnych testów funkcjonalnych**: up74 i up74+AA × PAL/NTSC × 64 KB/1088 KB RAM. Co najmniej 2738 ramek lotu na test, długie skręty w obie strony, nurkowanie/wznoszenie, kontrola kolejnych prezentacji i Esc pause/resume. Brak awarii; `functional-summary.json`.

To mocne potwierdzenie zgodności, **nie formalny dowód wszystkich stanów gry**. Zmiany nie obniżają rozdzielczości, nie zmniejszają odległości rysowania ani nie upraszczają gór; zachowują obliczany obraz dla tego samego wejścia. Różne planety po zimnym starcie mogą wynikać z innego momentu odczytu RANDOM. Nie testowano fizycznego Atari ani wszystkich możliwych akceleratorów.

## Zalecany sposób dalszej integracji

1. Przyjąć źródła i generator up74 na bazie v11 jako spójną podstawę 128 KB. Nie nakładać binarnie starszych banków.
2. Zachować cały zestaw nowych VBI, geometrii, rzutowania, rasteryzacji, fillu i pracy podczas oczekiwania. Dotychczasowe testy wskazują zgodność; duży zysk jest potwierdzony natywnie.
3. Osobno oceniać tylko dodatki, które nadal coś wnoszą: AA nie wykazało korzyści, pozostaje ewentualnie drobne Y z zachowaniem wyrównania. Nie dodawać historycznych procentów z v12/v13.
4. Nie integrować obecnej geometrii przyrostowej ani obecnego zestawu drzew. Ewentualny nowy generator drzew powinien powstać już dla rasteryzatora Solo i od początku uwzględniać koszt wyboru banku.
5. XEX wymaga osobnej aktualizacji relokacji: nowe banki 4 i 7, nowe źródła banków 2/3/5/9/10–14, kod rezydentny i znaczniki powrotów. Stary builder v11 jawnie zakłada niezmienione banki poza 5/6/8/9, więc nie można podstawić mu nowego ROM-u i uznać portu za gotowy. W tym audycie nie wydano nowego XEX-a.
6. Zachować poprawkę wskaźników muzyki XEX z v11 oraz test przejścia poziomu. Przy większych cartach nie zajmować kodu miksera `$9D3B–$9FD4` ani czynnej geometrii w banku 2. Bajty `$FF` w banku 3 `$963A–$97F0` nie są automatycznie wolne: są czytane przed lotem.

## Artefakty i odtworzenie

- `reproduction-summary.json`, `native-reproduction/`: niezależne odtworzenie wyników Solo.
- `package/results/full155_up74_*.json`: dostarczone 620 obserwacji; historyczna referencja oryginału/v11: `release-v11/results/v11/summary.json` w katalogu projektu.
- `native-aa-full/`, `aa-study-summary.json`: pełny nowy eksperyment AA i porównanie z odpowiadającym podzbiorem up74.
- `validation/`, `check-quick.log`, `multiply-exhaustive.log`, `sound-queue-fuzz.json`: zgodność i koszty.
- `incremental-cost.json`, `tree-profile.json`, `fresh-pipeline-*.json`: porównania opcji.
- `build_variants.py`, `build_y_aligned.py`, `build_trees.py`, `build_trees_after_cull.py`: lokalne generatory prób. Pliki w `build/` to **eksperymenty, nie nowe wydanie**.
- `native_study.py`, `capture_native.py`, `verify_fresh.py`, `native_functional.py`, `analyze_aa.py`: procedury reprodukcji i weryfikacji.

Python używa `tools/up38_audit_deps` w `PYTHONPATH`, MADS z `tools/mads/bin/windows_x86_64/mads.exe`, emulator z `tools/bridge/AltirraBridge-nightly-windows-x86_64`. Cztery niezależne procesy emulatora; wyniki z czasu Atari, nie czasu komputera gospodarza. Katalog roboczy może zawierać logi nieudanych pierwszych adaptacji harnessu; nie są one oznaczone jako zaliczone testy. Żaden odrzucony wariant nie trafił do repozytorium.
