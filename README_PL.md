# Rescue on Fractalus! — optymalizacja Atari XL/XE PAL

Stan przekazania: 21.10.2026. Aktualne wydanie: v6, 128 KiB XEGS (typ CART 14). Wydanie v3 64 KiB zachowano.
Wynik czterech lotów: oryginał 6,553531 FPS; v1 6,779769; v2 7,115256;
v3 7,192973; v4 7,316840; v5 7,367256; v6 7,691000 FPS. Zysk v6: 17,36% względem oryginału, 4,39% względem v5.
To pomiary określonych lotów, nie gwarancja FPS dla każdego terenu.

Gotowa gra: dist/Rescue on Fractalus! - PAL optimized v6 128KB.car
Oryginalny obraz: original/Rescue on Fractalus!.rom (niezmieniony).
Odtworzenie gry: python scripts/rebuild_v6.py --mads ŚCIEŻKA_DO_MADS
Instrukcja środowiska: docs/ODTWORZENIE_PL.txt
Mapa kodu i istotne pułapki: docs/KONTYNUACJA_PL.txt
Dalsze kierunki: docs/DALSZE_KIERUNKI_PL.txt
Historyczny audyt v5 (punkty 1–4 wdrożone w v6, 5–8 odłożone): docs/OPCJE_OPTYMALIZACJI_V5_PL.md
Raport bieżącego wydania: docs/WYDANIE_V6_PL.txt
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
