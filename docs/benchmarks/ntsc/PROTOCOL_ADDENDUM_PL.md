# Uzupełnienie protokołu: naturalne zakończenie lotu przed 60 s

[English](PROTOCOL_ADDENDUM.md) · [Polski](PROTOCOL_ADDENDUM_PL.md)

Regułę dopisano po 47 ukończonych próbach, gdy 48. scenariusz (v9, próba 24, START po 3357 klatkach menu) zakończył lot przed minutą. To zmiana obsługi zdarzenia w toku badania, a nie element pierwotnego planu. Nie zmieniono liczby prób 155 na wersję, harmonogramu ani doboru danych wejściowych.

Odtworzenie wykazało zmianę trybu gry z 2 na 0 przy instrukcji $B3C4 (STA $4A), po około 32,2484 s pomiaru. Poprzedza ją standardowa ścieżka $A444 → $B3B6 po ustawieniu flagi $063A. Następuje sekwencja wygaszania/kończenia rozgrywki. Nie ustalono w tym badaniu, który konkretny obiekt lub zdarzenie rozgrywki ustawił flagę. Nie należy na tej podstawie deklarować błędu v9.

## Obowiązująca reguła

- Mierzymy FPS podczas lotu przez maksymalnie 60 sekund albo do pierwszego wyjścia z trybu lotu, jeżeli nastąpi wcześniej.
- Każda taka próba pozostaje w średniej; nie losujemy zastępczej mapy.
- FPS obliczamy z pełnych odstępów między ukończonymi obrazami, do ostatniego ukończonego obrazu w trybie lotu. Animacja zakończenia gry i czas bez nowych obrazów terenu nie wchodzą do mianownika.
- Zapisujemy dokładny moment zmiany trybu, liczbę obrazów, czas ostatniego ukończonego obrazu oraz flagę complete_window=false dla niezrealizowanych w całości okien.
- Każdy punkt 15/30/60 s, którego lot nie osiągnie, otrzymuje wynik z całego dostępnego odcinka lotu i jawne oznaczenie skrócenia. To nie jest wynik pełnego okna o tej długości.
- Brak jakiegokolwiek mierzalnego odstępu lub zatrzymanie renderera przy nadal aktywnym trybie 2 pozostaje błędem wymagającym osobnej diagnozy; nie jest automatycznie usuwane.
- W raporcie podajemy liczbę skróconych lotów i zakres czasów. Wynik oznacza średni FPS z lotów trwających DO 60 s, a nie wyłącznie średni FPS pełnych minut.

Pozostałe warunki, oryginalny kod gier i rozgrzewka 170 klatek nie zmieniają się. Monitorowanie zapisu trybu jest punktem kontrolnym debuggera, nie zmianą pamięci gry. 47 wcześniej ukończonych prób pozostaje poprawnymi obserwacjami według tej reguły.

To uzupełnienie należy jawnie ujawnić przy interpretacji wyników. Badanie nie jest od tego momentu testem w całości zarejestrowanym z góry dla nowej definicji wyniku. Przedziały ufności opisują uzupełniony scenariusz; nie rozwiązują kwestii doboru scenariusza po rozpoczęciu badania. Nie analizujemy wyłącznie lotów, które przetrwały minutę, bo byłaby to selekcja zależna od rozgrywki.
