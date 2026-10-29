# Pomysły ilmenita — stan wdrożenia

Tabela FPS pokazuje łączny efekt zmian wdrożonych w v12 i v13, wyłącznie względem oryginału i v11. Nie przypisujemy całego zysku osobno każdej małej zmianie. Oryginalna paczka ilmenita bazowała na naszym v10.1, a nie v11.

| Pomysł | Stan / wersja | Efekt lub powód decyzji |
|---|---|---|
| Gotowe drzewa podziału szerokości | **v13: 512 KB i 1 MB** | Znikają obliczenia środkowego X i sterowanie drzewem; dokładny fallback. FPS: tabela poniżej. |
| Selektywne testy zasłaniania w drzewach | **v13** | Odrzucanie zasłoniętych fragmentów przed rysowaniem; efekt ujęty w łącznym wyniku v13. |
| Dokładny skrót fill `$AA` | **v12** | Krótsze wypełnianie powtarzalnego wzoru; brak osobnej pełnej serii FPS tylko tego skrótu. |
| Dalsze usunięcie obsługi Y | Częściowo v11, szerzej **v12** | d0–d4 bez zbędnych operacji, Y=5 przed fallbackiem; efekt ujęty w łącznym wyniku danej wersji. |
| Grupowanie geometrii 33–44 | **v12** | Mniej pracy przy przygotowaniu geometrii; brak osobnej pełnej serii FPS tylko tej zmiany. |
| Adaptacja pustego widoku / sky reuse | **Nie przyjęto badanej adaptacji** | Nasz wariant zwiększał koszt renderera, więc został usunięty; nie jest to ocena każdego cache z paczki. |
| Bankowane drzewo dzielenia | **Nie przeniesiono** | Prosta otoczka bankowania pochłania przewidywaną oszczędność względem kodu inline w v11; dalszy wariant inline pozostaje pomysłem. |
| GTIA / GR.10 | **Poza zakresem tej linii** | Zmienia grafikę i próbkowanie; nie jest przezroczystą optymalizacją GR.7. |
| Dawne PMG, audio, interpolacja, geometria, clipping | Już w bazie **≤v10.1/v11** | Elementy odziedziczone z naszego projektu; nie liczymy ich jako nowego wkładu ani ponownego zysku. |

| System | Wersja / cartridge | FPS | Zysk względem oryginału | Zysk względem v11 |
|---|---|---:|---:|---:|
| PAL | v12 / 128 KB | **8.9329** | **+42.43%** | **+1.71%** |
| PAL | v13 / 512 KB | **9.2791** | **+47.95%** | **+5.65%** |
| PAL | v13 / 1 MB | **9.3856** | **+49.65%** | **+6.86%** |
| NTSC | v12 / 128 KB | **8.1499** | **+45.75%** | **+1.83%** |
| NTSC | v13 / 512 KB | **8.4698** | **+51.48%** | **+5.83%** |
| NTSC | v13 / 1 MB | **8.5354** | **+52.65%** | **+6.65%** |

Referencje: PAL: oryginał **6.2717 FPS**, v11 **8.7829 FPS**; NTSC: oryginał **5.5915 FPS**, v11 **8.0031 FPS**.

FPS to wynik ważony 50/50 dla lotu prosto i z nurkowaniem. Oryginał i v11: pełne historyczne serie po 155 lotów na scenariusz i system; v12 i każdy wariant v13: po 155 lotów na system, podzielonych na 78 prosto i 77 z nurkowaniem. Zysk = (FPS danej wersji / FPS referencji − 1) × 100%, liczony z niezaokrąglonych średnich. Procentów poszczególnych etapów nie sumujemy.

512 KB ma również XEX dla 1 MB RAM. Układ 1 MB CAR potrzebowałby 126 stron po 16 KB, a obecny loader ma 64; dlatego nie dostarczamy jego XEX. Oba cartridge’e wymagają tylko 64 KB RAM.

[Pełne pomiary](benchmarks/V13_REPORT_PL.md) · [Opis techniczny](terrain/COMPILED_TREES_PL.md)
