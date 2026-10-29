# Metodyka FPS v13

Każdy wariant cartridge’a ma 155 niezależnych zimnych startów PAL i 155 NTSC: po 78 lotów prosto i 77 z nurkowaniem na system. Oba warianty pracują równolegle, po dwa procesy każdy, łącznie cztery izolowane emulatory. Stock 800XL/64 KB, historia wyłączona, tempo hosta nieograniczone. Zachowano ten sam zamrożony przydział startów/scenariuszy co v12.

Po 170 ramkach rozgrzewki liczymy pełne odstępy prezentacji terenu B516 w nominalnym oknie 60 s, według zegara Atari. Naturalne wcześniejsze końce pozostają. Nurkowanie: 1 s joystick w górę i 3 s neutralnie. Terminy cykli są dokładne. Ograniczone paczki poleceń zachowują zdarzenia i RAM właściwy dla końca próby. Bez przenoszenia stanów między ROM-ami, odrzucania wyników ani ponawiania poprawnych niewygodnych prób.

Łączne FPS = 0,5 * średnia FPS lotów prosto + 0,5 * średnia FPS nurkowania. Zysk jest ilorazem średnich łącznych. Oryginał zachowuje historyczną referencję 155+155 lotów na system; v12 i oba v13 mają te same wybrane 155 planów startu, a początkowe mapy są zgodne.

Przedziały 95%: 20 000 replik percentylowego bootstrapu, ziarno 2026102913; losujemy starty w grupach 78/77, parując v12 i oba v13 oraz zachowując współzależność z oryginałem z nurkowaniem. Historyczny oryginał prosto ma niezależny plan i jest resamplowany niezależnie.

Dane: results/v13/512KB i results/v13/1024KB oraz results/v12 i historyczne referencje oryginału. Obliczenia: scripts/report_v13.py. Testy funkcjonalne XEX są osobne; seria FPS dotyczy CAR. Emulator nie był łatany. Nowe pomiary wymagają świeżych katalogów wynikowych.
