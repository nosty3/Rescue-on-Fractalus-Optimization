# Metodyka FPS v12

155 niezależnych zimnych startów na system: 78 lotów prosto i 77 z nurkowaniem. Cztery izolowane procesy Altirry, 800XL/64 KB, PAL albo NTSC, historia CPU wyłączona i tempo hosta bez ograniczenia. 170 ramek rozgrzewki, potem nominalne okno 60 s domknięte do odstępu prezentacji B516. Zegar emulowanego Atari, nie czas komputera. Nurkowanie: 1 s joystick w górę co 4 s, poza tym neutralnie.

Plan startów i scenariuszy zamrożony przed serią. Wynik = 0,5 * średnia FPS lotów prosto + 0,5 * średnia FPS nurkowania. Nie jest to prosta średnia 155 próbek o nierównych wagach scenariuszy. Zachowujemy naturalne końce, bez odrzucania skrajnych wyników i bez przenoszenia stanów między ROM-ami.

Sterownik wysyła ograniczone paczki poleceń, zachowuje wszystkie znaczniki prezentacji i terminy joysticka oraz RAM właściwy dla końca próby. Emulator nie został zmodyfikowany. Oryginał/v11: wcześniejsze pełne dane po 155 prób na scenariusz/system. Historyczny lot prosto oryginału ma niezależny plan startów; nie parujemy go sztucznie po numerze próby.

Bootstrap 95%: 20 000 replik, ziarno 2026102912; całe starty losowane osobno w grupach 78/77, zachowane zależności v11 i oryginału z nurkowaniem; oryginał prosto osobno. Dane: results/v12/plan.json, flights.jsonl, summary.json i analysis-plan.json. Raport V12_REPORT_PL.md.

Przy nowym pomiarze użyj świeżego katalogu wyjściowego; nie nadpisuj publikowanych obserwacji. Nowy sterownik: scripts/benchmark_current.py --help. Mostek instaluj pod tools/bridge lub ustaw FRACTALUS_BRIDGE_DIR. XEX ma osobną kontrolę poprawności; publikowane FPS dotyczą CAR.
