# Gotowe drzewa podziału v13

Generator ilmenita wyznacza pozycje środkowego X i kolejność przejścia dla znanej szerokości odcinka. Zaburzenia wysokości, nasiona, zaokrąglenia, clipping i rozdzielczość pozostają dokładne. Nieobsługiwane szerokości korzystają z dokładnego fallbacku v12. Lewy clipping ma osobne procedury z powodu innych zaokrągleń.

512 KB ma 46 specjalizacji w 47 dodatkowych bankach 8 KB; 1 MB — 86 w 111 bankach. Zagnieżdżone zestawy pochodzą z osobnego wcześniejszego profilu 40 scen, a nie pełnego pomiaru v13. To heurystyka, nie dowód najlepszego przydziału banków.

Wybór następuje raz na odcinek: tabele w nieużywanym starym fill banku 2, selektor $9C42, wejście $9858, fallback $9FEF. Projekcja Fable pod $984F jest zachowana. Większe procedury przechodzą między bankami z zachowaniem A/P. Każdy przyjęty piksel respektuje HD/lazy clear v12; helpery i tabele wierszy są lokalne w każdym fragmencie. Synchronizacja buforów i oczekiwanie względem wiązki pozostają.

Funkcja `source()` generatora jest niezmieniona względem paczki ilmenita przygotowanej z AI; dostosowano ścieżkę projektu i tworzenie katalogu przy imporcie. Integrację z v12 i rozszerzony XEX przygotowała Astra. Pochodzenie: `src/v13/provenance.json`.

## XEX 512 KB

62 strony rozszerzenia po 16 KB zawierają bank 8 KB i kopię stałego kodu 8 KB. Wymagane rozszerzenie 1 MB, 1088 KB łącznie. PB1/2/3/5/6/7 wybierają stronę; PB0 zachowuje włączony OS. BASIC i self-test są wyłączane przed bankowaniem; zgodne rozszerzenie zatrzaskuje ich stan sterowania. Loader sprawdza 64 różne strony.

Część nowych prawidłowych wartości PORTB jest mniejsza niż $80. Strażnik VBI akceptuje więc każdy niezerowy znacznik; zero oznacza bank 2. Zachowano 9-bajtową obsługę stosu Esc i obie poprawione tablice melodii. Przeszły: start/sterowanie/pauza PAL/NTSC, cztery kontrolowane przejścia poziomu, 160 porównań CAR/XEX, wszystkie 58 banków VBI i odmowa przy 320/576 KB.

Cartridge 1 MB potrzebowałby w tym układzie 126 stron, ponad limit 64. Jego XEX wymaga osobnego projektu pakowania/mapowania; nie jest to dowód ogólnej niemożliwości. Same cartridge’e wymagają tylko 64 KB RAM.

Naprawa bankowania z 2026-10-29: fallback przełącza bank pod `$9FEF` i kontynuuje w banku 5 pod `$9FF2`. Oba miejsca są sprawdzane jako wolna przestrzeń. Mikser `$9D3B..$9FD4` i dyspozytor geometrii pozostają chronione. [Przyczyna i regresja](V13_SOUND_FIX_PL.md).
