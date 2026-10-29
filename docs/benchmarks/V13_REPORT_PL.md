# Pełne pomiary v13

Wynik 50/50 to połowa średniej lotów prosto i połowa średniej nurkowania. Każdy wariant v13: 155 zimnych startów PAL i 155 NTSC, po 78 prosto i 77 z nurkowaniem, nominalnie 60 s. Łącznie 620 nowych lotów w czterech izolowanych emulatorach. Ten sam plan co v12; wszystkie początkowe mapy są zgodne. Oryginał zachowuje pełną historyczną referencję 155+155 na system. Naturalne wcześniejsze końce pozostają w danych. FPS dotyczy CAR; XEX przeszedł osobną walidację funkcjonalną.

| System | Wariant | FPS | Zysk względem oryginału | Zysk względem v11 |
|---|---|---:|---:|---:|
| PAL | 512 KB | **9.2791** | **+47.95%** | **+5.65%** |
| PAL | 1 MB | **9.3856** | **+49.65%** | **+6.86%** |
| NTSC | 512 KB | **8.4698** | **+51.48%** | **+5.83%** |
| NTSC | 1 MB | **8.5354** | **+52.65%** | **+6.65%** |

### PAL

Oryginał: 6.271731 FPS; v11: 8.782928 FPS.

- 512 KB: 9.279064 FPS, 95% [9.197611, 9.360884]; v11 +5.6489%; wcześniejsze końce 9/155.
- 1 MB: 9.385565 FPS, 95% [9.311797, 9.459674]; v11 +6.8615%; wcześniejsze końce 7/155.

### NTSC

Oryginał: 5.591516 FPS; v11: 8.003108 FPS.

- 512 KB: 8.469807 FPS, 95% [8.399788, 8.540815]; v11 +5.8315%; wcześniejsze końce 8/155.
- 1 MB: 8.535392 FPS, 95% [8.463765, 8.607318]; v11 +6.6510%; wcześniejsze końce 5/155.

20 000 replik bootstrapu, ziarno 2026102913. Te same indeksy startów zachowują parowanie obu wariantów v13; losowanie osobno w grupach 78/77. Zachowana korelacja z oryginałem z nurkowaniem; historyczny oryginał prosto losowany niezależnie. Bez odrzucania wyników i przenoszenia stanów. Wszystkie początkowe mapy sprawdzone haszem są zgodne. Referencja v11 pochodzi z pełnych historycznych serii po 155 lotów prosto i 155 z nurkowaniem na system. Zysk względem v11 jest ilorazem średnich 50/50; nie podajemy dla niego przedziału ufności. Badanie opisuje dwa automatyczne scenariusze, nie całą rozgrywkę.

512 KB: 39.12 min czasu rzeczywistego; serie równoległe, po dwa procesy każda.
1 MB: 39.17 min czasu rzeczywistego; serie równoległe, po dwa procesy każda.

[Dane](../../results/v13/) · [Metodyka](METHOD_PL.md) · [Walidacja](../../results/v13/validation/)

Walidacja: po 80 scen dla obu wariantów, 1500 losowych odcinków, 24 krótkie loty kontrolne v12/v13 z pauzą, skrętami i strzelaniem. XEX: PAL/NTSC, 4 kontrolowane przejścia poziomu, 160 porównań relokacji, 58 banków VBI i odmowa przy 320/576 KB. To testy emulatora i modelu CPU; nie certyfikacja sprzętu.
