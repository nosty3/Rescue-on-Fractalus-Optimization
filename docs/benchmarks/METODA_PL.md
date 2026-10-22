# Aktualne pomiary PAL i NTSC

Wyniki główne pochodzą z dwóch serii po **155 lotów oryginału i 155 lotów v9**, osobno dla PAL i NTSC. Źródła to [raport PAL](pal/RAPORT_PAL_PL.md), [protokół PAL](pal/PROTOKOL_PL.md), [raport NTSC](ntsc/RAPORT_NTSC_PL.md) oraz [uzupełnienie protokołu NTSC](ntsc/UZUPELNIENIE_PROTOKOLU_PL.md).

| System | Oryginał FPS | v9 FPS | Zysk | 95% przedział ufności zysku |
| --- | ---: | ---: | ---: | --- |
| PAL | 6,4421 | 7,5623 | 17,39% | 16,46–18,32% |
| NTSC | 5,8043 | 6,8977 | 18,84% | 17,90–19,78% |

## Warunki i licznik

Każdy lot uruchamiano w świeżym procesie Altirry, od natywnego zimnego startu właściwego cartridge'a: Atari 800XL, 64 KB, bez akceleratora. Nie przenoszono stanu ani nie poprawiano pamięci gry. Joystick pozostawał wycentrowany, bez strzelania, skrętów, nurkowania i dopalacza.

Zamrożony harmonogram używa ziarna 2026102303 i 155 różnych momentów START dla każdej wersji, losowanych bez zwracania z 3000–3599 ramek menu. W 31 blokach przeplatano po pięć prób obu wersji. PAL powtarza ten sam harmonogram liczony w ramkach; nie oznacza to identycznych map pomiędzy standardami lub wersjami.

Po pierwszym wejściu `$A32E` zwalniano START i wykonywano 170 ramek rozgrzewki: około 3,41 s PAL i 2,84 s NTSC. Pomiar liczy pełne odstępy pomiędzy ukończonymi obrazami przy `$B516`. Czas pochodzi z taktów emulowanego Atari, z zegarem 1 773 447,5 Hz PAL lub 1 789 772,5 Hz NTSC, i obejmuje DMA oraz przerwania. FPS = liczba pełnych odstępów / czas tych odstępów; nie jest częstotliwością VBI ani szybkością działania komputera gospodarza.

Okna 15/30/60 sekund są zagnieżdżonymi fragmentami jednego lotu. Domyka się pierwszy pełny odstęp po limicie. Gdy gra naturalnie kończy lot wcześniej, liczy się pełne odstępy przed opuszczeniem trybu lotu, bez animacji końcowej. Taka próba pozostaje w średniej; nie odrzucano ekstremów ani krótszych lotów. Dotyczyło to PAL: 3 oryginałów i 4 v9; NTSC: po jednym locie obu wersji.

## Równoległość i analiza

NTSC rozpoczęto sekwencyjnie; po 86 lotach pozostałe 224 wykonano równolegle po porównaniu czterech pełnych scenariuszy 60 s. PAL wykonywano czterema procesami po porównaniu czterech scenariuszy 15 s sekwencyjnie i równolegle. W kontrolach wymagano zgodności zdarzeń pomiarowych i RAM. Procesy miały osobne porty, tokeny i pliki; agregat zapisywano w kolejności planu. Kontrole nie należą do głównej średniej.

Główną statystyką jest średnia FPS poszczególnych lotów, z jednakową wagą każdego lotu. Zysk to `100 × (średnia_v9 / średnia_oryginału − 1)`. Nie jest średnią procentów z arbitralnie sparowanych map. Liczebność NTSC wybrano po pilocie, a dla PAL ustalono z góry taką samą. Sprawdzono również wynik ważony czasem i bootstrap warstwowy 50 000 replikacji. Regułę naturalnego końca doprecyzowano po pierwszych 47 lotach NTSC; dla PAL była ustalona przed pomiarem. Szczegóły i ograniczenia tego uzupełnienia zachowano w raporcie NTSC.

Przedziały ufności są przybliżone i dotyczą rozkładu scenariuszy tego protokołu. Nie dowodzą wydajności we wszystkich dolinach, skrętach, poziomach czy misjach. Ta sama wersja może mieć inny FPS na innej mapie. Nie należy utożsamiać różnicy pomiędzy dwoma krótkimi lotami ze zmianą kodu.

## Pliki i badania historyczne

- [Dane PAL](../../results/pal_isolated_main/) i [dane NTSC](../../results/ntsc_isolated_main/) zawierają plan, poszczególne próby, podsumowanie i wynik kontroli spójności.
- [Walidacja PAL](../../results/pal_parallel_validation/validation.json) i [walidacja NTSC](../../results/ntsc_parallel_validation/validation.json) dokumentują kontrolę równoległości.
- [charts/](charts/) zawiera angielskie PNG i SVG obu serii, użyte w README.
- [history/](history/), [ntsc_cold_20x2/](ntsc_cold_20x2/), [ntsc_repro_audit/](ntsc_repro_audit/), [ntsc_isolated_pilot/](ntsc_isolated_pilot/) i [ntsc_parallel_validation/](ntsc_parallel_validation/) opisują dochodzenie do obecnej metody.

Historyczne wyniki krótkich lotów, wspólnych stanów, średnich obciętych i zestawu czterech lotów PAL nie zastępują aktualnej tabeli. Stare ścieżki, numery wersji i zalecenia występujące w tych badaniach odnoszą się do momentu ich wykonania; dawne pliki można odzyskać z odpowiedniego commitu. Surowych zrzutów RAM i screenów nie publikujemy.
