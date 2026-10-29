# Pomysły ilmenita — stan wdrożenia

Zyski FPS dotyczą całych buildów; nie przypisujemy ich osobno każdej małej zmianie. Oryginalna paczka ilmenita bazowała na naszym v10.1, a nie v11.

| Pomysł | Stan / wersja | Zysk lub powód decyzji |
|---|---|---|
| Gotowe drzewa podziału szerokości | **v13: 512 KB i 1 MB** | Znikają obliczenia środkowego X i sterowanie drzewem; dokładny fallback. FPS: tabela poniżej. |
| Selektywne testy zasłaniania w drzewach | **v13** | Część tej samej integracji; na osobnych 40 scenach cały potok zużywa o 5,48% / 6,59% mniej cykli niż v12. To nie procent FPS. |
| Dokładny skrót fill `$AA` | **v12** | Trafienie: około 3405 → 917 cykli fill; brak osobnej pełnej serii FPS tylko tego skrótu. |
| Dalsze usunięcie obsługi Y | Częściowo v11, szerzej **v12** | d0–d4 bez zbędnych operacji, Y=5 przed fallbackiem; część łącznego zysku v12. |
| Grupowanie geometrii 33–44 | **v12** | Średnio 176,69 cyklu mniej na przygotowanie geometrii; brak osobnego pełnego FPS. |
| Adaptacja pustego widoku / sky reuse | **Nie przyjęto badanej adaptacji** | Nasz wariant dodał około 0,154% kosztu renderera. Usunięty; nie jest to ocena każdego cache z paczki. |
| Bankowane drzewo dzielenia | **Nie przeniesiono** | Względem inline Fable około 16 cykli rezerwy, a prosta otoczka kosztuje około 33; dalszy wariant inline pozostaje pomysłem. |
| GTIA / GR.10 | **Poza zakresem tej linii** | Zmienia grafikę i próbkowanie; nie jest przezroczystą optymalizacją GR.7. |
| Dawne PMG, audio, interpolacja, geometria, clipping | Już w bazie **≤v10.1/v11** | Elementy odziedziczone z naszego projektu; nie liczymy ich jako nowego wkładu ani ponownego zysku. |

| System | Wariant | FPS | Zysk względem oryginału | Zysk względem v12 |
|---|---|---:|---:|---:|
| PAL | 512 KB | **9.2791** | **+47.95%** | **+3.87%** |
| PAL | 1 MB | **9.3856** | **+49.65%** | **+5.07%** |
| NTSC | 512 KB | **8.4698** | **+51.48%** | **+3.93%** |
| NTSC | 1 MB | **8.5354** | **+52.65%** | **+4.73%** |

v12 jako cały pakiet dodał względem pełnej referencji v11 +1,71% PAL i +1,83% NTSC. Zawiera także własne skrócenia skanów Astry. Te procenty nie są osobnymi zyskami każdego wiersza tabeli. Wstępne 17,87% dotyczyło izolowanych odcinków względem v11, bez pełnej integracji cache i bez pomiaru FPS. Nie sumujemy ani nie mnożymy go przez wyniki końcowe.

512 KB ma również XEX dla 1 MB RAM. Układ 1 MB CAR potrzebowałby 126 stron po 16 KB, a obecny loader ma 64; dlatego nie dostarczamy jego XEX. Oba cartridge’e wymagają tylko 64 KB RAM.

[Pełne pomiary](benchmarks/V13_REPORT_PL.md) · [Opis techniczny](terrain/COMPILED_TREES_PL.md)
