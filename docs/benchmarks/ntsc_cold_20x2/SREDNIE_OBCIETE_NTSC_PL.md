Dokument badawczy zachowany historycznie. Dawne ścieżki i wyniki dotyczą opisanego eksperymentu; aktualną implementację opisuje docs/OPTYMALIZACJE_PL.md, a wyniki zbiorcze docs/benchmarks/METODA_PL.md (ścieżki od katalogu głównego repozytorium).

# NTSC: średnie po odrzuceniu skrajnych wyników

Dla każdej serii i każdej wersji osobno posortowano 20 wyników FPS, odrzucono 3 najniższe i 3 najwyższe, a następnie obliczono średnią arytmetyczną pozostałych 14. Nie wykonywano nowych pomiarów; źródłowy benchmark.json pozostaje bez zmian.

| Seria | Oryginał: 20 prób | Oryginał: 14 prób | v9: 20 prób | v9: 14 prób | Zysk po odrzuceniu skrajnych |
|---|---:|---:|---:|---:|---:|
| 1 | 5,7764 | 5,7298 | 6,7344 | 6,7319 | 17,4882% |
| 2 | 5,7708 | 5,7289 | 7,0054 | 7,0097 | 22,3569% |

## Różnica między seriami

- original: seria 2 minus seria 1 = -0,0010 FPS (-0,0168%).
- v9: seria 2 minus seria 1 = 0,2778 FPS (4,1265%).

## Odrzucone próby

Numery prób odnoszą się do numeracji 1–20 w danej serii.

- Seria 1, original: najniższe: 6 (5,4295 FPS), 9 (5,4836 FPS), 17 (5,5140 FPS); najwyższe: 4 (6,1714 FPS), 10 (6,2309 FPS), 8 (6,4817 FPS).
- Seria 1, v9: najniższe: 6 (6,4227 FPS), 9 (6,4583 FPS), 4 (6,4655 FPS); najwyższe: 16 (7,0031 FPS), 19 (7,0419 FPS), 15 (7,0497 FPS).
- Seria 2, original: najniższe: 18 (5,5018 FPS), 13 (5,5018 FPS), 3 (5,5496 FPS); najwyższe: 4 (5,9989 FPS), 14 (6,2656 FPS), 7 (6,3944 FPS).
- Seria 2, v9: najniższe: 20 (6,4674 FPS), 4 (6,5177 FPS), 19 (6,5915 FPS); najwyższe: 14 (7,3578 FPS), 13 (7,3905 FPS), 17 (7,6483 FPS).

Odrzucanie skrajnych wyników nie usunęło rozbieżności średnich v9 między seriami. Jest to średnia obcięta (po 15% z każdej strony), a nie średnia ze wszystkich normalnych uruchomień gry. Skrajnych prób nie uznano za błędne — pominięto je zgodnie z wybraną metodą obliczenia.
