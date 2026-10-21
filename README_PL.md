# Rescue on Fractalus! — optymalizacja Atari XL/XE PAL

Stan przekazania: 21.10.2026. Aktualne wydanie: v3, 64 KiB XEGS (typ CART 13).
Wynik czterech lotów: oryginał 6,553531 FPS; v1 6,779769; v2 7,115256;
v3 7,192973 FPS. Zysk v3: 9,76% względem oryginału, 1,09% względem v2.
To pomiary określonych lotów, nie gwarancja FPS dla każdego terenu.

Gotowa gra: dist/Rescue on Fractalus! - PAL optimized v3.car
Oryginalny obraz: original/Rescue on Fractalus!.rom (niezmieniony).
Odtworzenie gry: python scripts/rebuild_releases.py --mads ŚCIEŻKA_DO_MADS
Instrukcja środowiska: docs/ODTWORZENIE_PL.txt
Mapa kodu i istotne pułapki: docs/KONTYNUACJA_PL.txt
Dalsze kierunki: docs/DALSZE_KIERUNKI_PL.txt
Raport bieżącego wydania: docs/WYDANIE_V3_PL.txt
Lista plików i SHA-256: docs/backup-manifest.json

Repozytorium zawiera wybrany zestaw źródeł, wydań i wyników. Celowo nie ma
screenów, dumpów RAM, stanów emulatora, pakietów narzędzi, tokenów i logów
lokalnego serwera. Bez dawnych stanów nie da się odtworzyć dokładnie tych
samych lotów; można odtworzyć ROM-y i zebrać nowy zestaw pomiarowy.
Dokumenty historyczne opisują stan prac z chwili ich powstania. Ich stare
ścieżki lokalne mogą wskazywać pominięte pliki; bieżący przewodnik jest tutaj.
Nie wykonano tłumaczeń. Polskie notatki i raporty oznaczono w nazwie _PL.
Oryginalny ROM jest materiałem wejściowym właściciela projektu; nie nadano
mu nowej licencji ani nie stwierdza się prawa do jego publicznej dystrybucji.
