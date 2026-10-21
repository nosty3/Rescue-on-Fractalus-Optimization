# Wydanie v9 — niewielka optymalizacja PMG

21.10.2026. Atari XL/XE PAL, 64 KiB RAM, XEGS 128 KiB / CART 14.

Wydano dokładnie przetestowany wariant PMG, bez dalszych zmian binarnych.
Użytkownik zaakceptował ten konkretny zysk poniżej dotychczasowego progu
+0,05 FPS, pod warunkiem małej złożoności i bezpieczeństwa. Nie zmieniono
automatycznie progu dla przyszłych eksperymentów.

## Wynik

v8: **7,720697 FPS**. v9: **7,764418 FPS**.
Różnica: **+0,043721 FPS (+0,566%)** w standardowym zestawie czterech lotów.
Nie wykonano ponownego pomiaru identycznego ROM-u przy samym nadaniu numeru
wydania. Wyniki i ograniczenia pierwszej serii są w PROBA_PMG_PL.md.
Trzy scenariusze zyskały, szybki lot w prawo nieco zwolnił. Nie jest to
gwarancja przyspieszenia każdego lotu ani wynik serii statystycznej.

## Zakres i bezpieczeństwo

- Pasek PMG $A55C: zapisuje tylko zmieniony odcinek. Dla starej wartości
  zero oraz danych poza zakresem 0..55 zachowuje pełne odrysowanie.
- Pętle 3/5 wierszy rozwinięto, a 21 wierszy kopiuje się po trzy na iterację.
- Bez zmiany formatu cartridge'a, jakości obrazu i matematyki terenu.
- Zachowano naprawę synchronizacji buforów z v8.
- Kod pomocniczy: bank 2, $83CA..$8470 i $84B0..$84F3. Nie nakłada się
  na clipping $8380..$83C9, osłonę $84A0..$84AE ani kontynuację $84FD.
  Wejścia są w VBI z już aktywnym bankiem 2; bank powrotny zachowuje
  istniejąca osłona przerwania. Brak nowych zmiennych i samomodyfikacji.

Weryfikacja obejmuje 5268 przypadków porównawczych CPU, 320 kontroli
spójności paska oraz zimny start, poziomy 10/26 i restarty z banków
rozszerzeń. Przed wydaniem dodatkowo porównano pierwszych 40 rzeczywistych
wywołań obsługi paska po zimnym starcie z oryginalną procedurą v8:
pierwsza zmiana 0→29 wykonała poprawne pełne odrysowanie, kolejne
aktualizacje zachowały zgodność całego RAM poza martwym stosem oraz
rejestrów i flag. Wynik: initialization.json.

To ograniczona, sprawdzona zmiana, ale nie dowód poprawności każdej
możliwej sekwencji rozgrywki. Testy odbyły się w modelu CPU i Altirrze
headless, nie na fizycznym Atari. Zalecany zimny start CAR v9; nie należy
przenosić starego save-state'u z arbitralnie niespójnym stanem PMG.

## Pliki i odtworzenie

Gotowy plik: dist/Rescue on Fractalus! - PAL optimized v9 128KB.car
ROM SHA256: `0c8226e1f58ad26b2a103cbf59c4b8b23fdb87caac0e22f2586a83513a859880`
Odtworzenie offline: `python scripts/rebuild_v9.py --mads ŚCIEŻKA_DO_MADS`.
Builder sprawdza zgodność ROM-u, CAR-a i łatki IPS do oryginalnego ROM-u.
Wcześniejsze wydania pozostają w dist. Historyczny raport pierwszej próby
nadal opisuje decyzję sprzed późniejszej zgody użytkownika na wydanie.

Nie wdrażano pozostałych pomysłów audytu PMG. Ich opis zachowano
w AUDYT_PMG_PL.md; nie należy traktować ich jako już przetestowanych poprawek.
