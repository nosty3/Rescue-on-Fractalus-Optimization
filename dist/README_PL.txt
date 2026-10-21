WY D A N I E   O P T Y M A L I Z O W A N E   P A L

Uruchom plik "Rescue on Fractalus! - PAL optimized.rom" jako kartridż,
tak samo jak dostarczony oryginał. Plik ma 64 KiB i ten sam układ banków.
Nie wymaga emulatora headless; headless służył do testów.
Zalecane ustawienie do porównania: Atari 800XL, 64 KiB, PAL, bez akceleratorów.
Zapisane stany gry z innego ROM-u nie zastępują testu zimnego startu.

fractalus-pal-optimized.ips to alternatywa dla gotowego ROM-u:
nałóż ją na kopię oryginalnego pliku o SHA-256 podanym w build-manifest.json.

Z katalogu projektu:
  python scripts/build_release.py
  python scripts/test_optimized_fast.py
  python scripts/test_release.py
  python scripts/test_release_random.py

Pomiar (tylko jeden bridge naraz):
  .\scripts\launch.ps1
  python scripts/benchmark_compare.py
  python scripts/stop.py

Narzędzia MADS, AltirraBridge i py65 są w tools/; nic nie trzeba instalować
systemowo. Dodatkowe biblioteki CPU-testów są w tools/pythonlib/.
Raport: ../docs/WYDANIE_V1_PL.txt
Wynik: około 6,55 -> 6,78 FPS (+3,4%) w czterech zmierzonych odcinkach PAL.
Nie jest to gwarantowany FPS wszystkich scen ani pełny test każdej misji.
