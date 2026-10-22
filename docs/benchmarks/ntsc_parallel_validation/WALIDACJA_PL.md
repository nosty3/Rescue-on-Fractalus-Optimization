# Walidacja czterech odizolowanych emulatorów

Użytkownik zezwolił na cztery równoległe procesy po potwierdzeniu zgodności z pomiarem sekwencyjnym. Bieżący pomiar zatrzymano po 86 ukończonych próbach; nieukończona próba zostaje wykonana ponownie z tym samym wejściem.

Wybrano cztery istniejące referencje z pilota: minimum i maksimum FPS okna 60 s osobno dla oryginału i v9. Uruchomiono je jednocześnie od natywnego BOOT, bez wczytywania stanów. Każdy emulator miał osobny proces, port przydzielony przez system, token, kontroler i pliki wynikowe.

Wszystkie cztery próby wykazały dokładną zgodność:

- liczb obrazów i taktów dla 15, 30 i 60 s;
- całych list odstępów między obrazami;
- pełnych 32 KB RAM przy wejściu do lotu, po rozgrzewce i na końcu pomiaru.

Wyniki maszynowe: `validation.json`. Procedura: `scripts/validate_ntsc_parallel.py`. Jest to walidacja tych czterech scenariuszy, a nie dowód poprawności emulatora we wszystkich sytuacjach.

Kontynuacja głównego badania: `scripts/benchmark_ntsc_parallel.py`. Maksymalnie cztery emulatory, zakończenie każdego bloku przed rozpoczęciem następnego, zapis agregatu przez jeden wątek w kolejności planu i atomowa podmiana pliku. Liczebność, zaplanowane momenty START i metoda liczenia FPS pozostają takie same. Czas rzeczywisty wykonania na PC nie wchodzi do obliczeń FPS — używane są takty emulowanego Atari.
