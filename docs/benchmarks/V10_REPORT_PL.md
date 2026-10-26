# v10 — plotter i pełne pomiary PAL/NTSC

[English](V10_REPORT.md) · [Polski](V10_REPORT_PL.md)

Wykonano 155 nowych lotów v10 na standard. Oryginał i v9 pochodzą z historycznych serii po 155 lotów; kontrolny 60-sekundowy lot v9 w każdym standardzie odtworzył te same zdarzenia i pamięć wejściową. Emulator ma ten sam SHA256. Nie powtarzano całych serii kontrolnych.

## Wyniki

| System | Oryginał FPS | v9 FPS | v10 FPS | Zysk do oryginału | Zysk do v9 |
|---|---:|---:|---:|---:|---:|
| PAL | 6.4421 | 7.5623 | 7.6359 | +18.53% | +0.0736 FPS (+0.97%) |
| NTSC | 5.8043 | 6.8977 | 6.9377 | +19.53% | +0.0400 FPS (+0.58%) |

## Metoda i niepewność

Każda próba: osobny proces, zimny start, Atari 800XL 64 KB stock, START według 155 pozycji v9 w zamrożonym planie 2026102303, 170 klatek rozgrzewki, joystick wycentrowany. Cztery emulatory zweryfikowano przez powtórzenie czterech 15-sekundowych prób sekwencyjnie i równolegle; zdarzenia i RAM były identyczne. Kontrole nie wchodzą do średnich.

Licznik B516 i czas emulowanego Atari obejmują DMA/VBI. Okna 15/30/60 s są zależnymi fragmentami lotu. Naturalny wcześniejszy koniec pozostaje w próbie. Każdy lot ma jednakową wagę. Bez usuwania skrajnych wartości. Kontrola integralności potwierdza zgodność planu, 155 prób na standard, hashe zdarzeń i FPS przeliczone z taktów.

Bootstrap warstwowy: 50 000 replikacji lotów w blokach po pięć; porównanie do oryginału traktuje serie jako niezależne. Dodatkowy przedział t-Studenta różnicy v10−v9 uwzględnia pary o tych samych momentach START. To parowanie harmonogramu, nie obietnica identycznych map lub przebiegu gry.

- PAL: 95% bootstrap zysku do oryginału 17.70–19.36%; 95% przedział średniej różnicy do v9 +0.0504–+0.0969 FPS. Identyczny RAM na wejściu: 155/155 par. Skrócone loty v10: 3/155.

- NTSC: 95% bootstrap zysku do oryginału 18.68–20.37%; 95% przedział średniej różnicy do v9 +0.0177–+0.0622 FPS. Identyczny RAM na wejściu: 155/155 par. Skrócone loty v10: 2/155.

Przedziały opisują tę metodę automatycznego lotu. Nie obejmują wszystkich poziomów, nurkowania czy skrętów. Testy nie były wykonywane na fizycznym Atari.

## Zmiana kodu i poprawność

Jedyna zmiana ROM względem v9 to bank 5. Tablice wierszy ROM mają efektywne podstawy $9700 i $9740 i nie powodują przekroczenia strony dla Y=104..151. Usunięto 48 zbędnych STY $B5 w wyspecjalizowanych ścieżkach, które odtwarzają Y ze stałej. Ogólne ścieżki zachowują tablice RAM. Bez zmian miksera, perspektywy, bankowania ani synchronizacji buforów.

Kod przeszedł 58 scen renderowania i kontynuacji, 6000 odcinków, 309 przypadków niskich wysokości, 2784 porównania tablic i 232 testy VBI. Średnia oszczędność w zestawie scen: 1248,09 cyklu na renderowanie i wypełnienie. Nie należy przeliczać jej wprost na cały FPS.

Kontrakt pamięci: B5 może różnić się po rendererze, a B4/B5 po dalszej geometrii; są traktowane jako wartości pomocnicze nieużywane przez dalsze badane obliczenia. Testy pomijają martwy stos. Rejestry i flagi na badanych wyjściach pozostają zgodne. To testy i audyt, nie formalny dowód wszystkich stanów gry.

ROM SHA256: `fde2166f28d768514a933a76654c9c3f9a583d4cdac182ed08aa14d15761bc37`. Źródło: `src/v10_plotter.asm`. Wyniki: `results/v10/`. Wykresy mają opisy angielskie.
