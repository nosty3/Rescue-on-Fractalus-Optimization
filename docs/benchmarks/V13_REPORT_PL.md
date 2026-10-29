# Pełne pomiary v13

Wynik 50/50 to połowa średniej lotów prosto i połowa średniej nurkowania. Każdy wariant v13: 155 zimnych startów PAL i 155 NTSC, po 78 prosto i 77 z nurkowaniem, nominalnie 60 s. Łącznie 620 nowych lotów w czterech izolowanych emulatorach. Ten sam plan co v12; wszystkie początkowe mapy są zgodne. Oryginał zachowuje pełną historyczną referencję 155+155 na system. Naturalne wcześniejsze końce pozostają w danych. FPS dotyczy CAR; XEX przeszedł osobną walidację funkcjonalną.

| System | Wariant | FPS | Zysk względem oryginału | Zysk względem v12 |
|---|---|---:|---:|---:|
| PAL | 512 KB | **9.2791** | **+47.95%** | **+3.87%** |
| PAL | 1 MB | **9.3856** | **+49.65%** | **+5.07%** |
| NTSC | 512 KB | **8.4698** | **+51.48%** | **+3.93%** |
| NTSC | 1 MB | **8.5354** | **+52.65%** | **+4.73%** |

### PAL

Oryginał: 6.271731 FPS; v12: 8.932929 FPS.

- 512 KB: 9.279064 FPS, 95% [9.197611, 9.360884]; v12 +3.8748%, 95% [+3.2950%, +4.4871%]; wcześniejsze końce 9/155.
- 1 MB: 9.385565 FPS, 95% [9.311797, 9.459674]; v12 +5.0670%, 95% [+4.5302%, +5.5941%]; wcześniejsze końce 7/155.

1 MB / 512 KB: +0.106501 FPS; +1.1478%, 95% [+0.4920%, +1.7715%].

### NTSC

Oryginał: 5.591516 FPS; v12: 8.149851 FPS.

- 512 KB: 8.469807 FPS, 95% [8.399788, 8.540815]; v12 +3.9259%, 95% [+3.3758%, +4.4819%]; wcześniejsze końce 8/155.
- 1 MB: 8.535392 FPS, 95% [8.463765, 8.607318]; v12 +4.7306%, 95% [+4.2554%, +5.2194%]; wcześniejsze końce 5/155.

1 MB / 512 KB: +0.065585 FPS; +0.7743%, 95% [+0.2748%, +1.2909%].

20 000 replik bootstrapu, ziarno 2026102913. Te same indeksy startów zachowują parowanie v12 i obu v13; losowanie osobno w grupach 78/77. Zachowana korelacja z oryginałem z nurkowaniem; historyczny oryginał prosto losowany niezależnie. Bez odrzucania wyników i przenoszenia stanów. Wszystkie początkowe mapy sprawdzone haszem są zgodne. Badanie opisuje dwa automatyczne scenariusze, nie całą rozgrywkę.

512 KB: 39.12 min czasu rzeczywistego; serie równoległe, po dwa procesy każda.
1 MB: 39.17 min czasu rzeczywistego; serie równoległe, po dwa procesy każda.

[Dane](../../results/v13/) · [Metodyka](METHOD_PL.md) · [Walidacja](../../results/v13/validation/)

Walidacja: po 80 scen dla obu wariantów, 1500 losowych odcinków, 24 krótkie loty kontrolne v12/v13 z pauzą, skrętami i strzelaniem. XEX: PAL/NTSC, 4 kontrolowane przejścia poziomu, 160 porównań relokacji, 58 banków VBI i odmowa przy 320/576 KB. To testy emulatora i modelu CPU; nie certyfikacja sprzętu.
