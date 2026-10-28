# Raport końcowy v11

[English](V11_REPORT.md) · [Polski](V11_REPORT_PL.md)

Wydanie v11 to dokładnie kandydat sentinel_depth_lazy_scan_fill z pełnych testów. Zmiana nazwy nie zmienia ROM-u. Poprawka wskaźników melodii dotyczy wyłącznie XEX.

Porównanie oryginału i najnowszego kandydata

Nowe pomiary: 155 lotów oryginału z nurkowaniem w PAL i 155 w NTSC. Cztery izolowane emulatory, zimny start każdej próby, 800XL/64K, 170 klatek rozgrzewki, do 60 sekund mierzonego lotu. Sterowanie: 1 s joystick w górę, 3 s neutralnie. Ten sam harmonogram startów co kandydata. Licznik B516 i zegar emulowanego Atari; naturalne wcześniejsze zakończenia uwzględnione, bez odrzucania wyników.

Lot prosto: wcześniej zmierzone wyniki, bez ponownego pomiaru. Historyczny oryginał miał niezależnie losowany harmonogram startów, więc nie jest to porównanie sparowane dla lotu prosto. Nurkowanie ma wspólny harmonogram. Zbiorcze FPS = średnia 50/50 obu scenariuszy; zysk = iloraz średnich minus 1. Każdy lot ma równą wagę.

PAL

| Scenariusz | Oryginał FPS | Kandydat FPS | Przyrost FPS | Zysk |
|---|---:|---:|---:|---:|
| Lot prosto | 6.4421 | 9.0779 | +2.6358 | +40.91% |
| Okresowe nurkowanie | 6.1013 | 8.4879 | +2.3866 | +39.12% |
| Średnia 50/50 | 6.2717 | 8.7829 | +2.5112 | +40.04% |

Wcześniejsze zakończenia: original_straight 3/155, original_steering 4/155, candidate_straight 5/155, candidate_steering 3/155

NTSC

| Scenariusz | Oryginał FPS | Kandydat FPS | Przyrost FPS | Zysk |
|---|---:|---:|---:|---:|
| Lot prosto | 5.8043 | 8.3120 | +2.5077 | +43.20% |
| Okresowe nurkowanie | 5.3787 | 7.6942 | +2.3155 | +43.05% |
| Średnia 50/50 | 5.5915 | 8.0031 | +2.4116 | +43.13% |

Wcześniejsze zakończenia: original_straight 1/155, original_steering 4/155, candidate_straight 2/155, candidate_steering 5/155

Candidate ROM SHA256: ec01982121b70baca35f04568617965c3164e716e0a5eb3c6ebcbb123566a868
Original ROM SHA256: 1eb18e2a1ff31f43871a5e4e21e73f61b7659177d33d2cdbb29f36530b9f4d68


Pełny test up38 i kandydata: lot prosto oraz sterowanie

Ukończono 1240 lotów: 4 konfiguracje × 2 standardy × 155 prób. Pilotów i kontroli transportu nie włączono do wyników.

METODA
Każdy lot: świeży proces Altirry, zimny start ROM-u, Atari 800XL/64 KB, bez akceleratorów. Ten sam zamrożony harmonogram 155 momentów START (plan v9, seed 2026102303), 170 ramek rozgrzewki, okno do 60 sekund emulowanego czasu. Docelowo cztery równoległe izolowane emulatory; 31 zamkniętych bloków. Incydent z dodatkowym procesem opisano niżej. Warianty korzystają z tych samych momentów START; sprawdzono równoważność RAM na wejściu wszystkich czterech konfiguracji w danej parze standard/próba, z udokumentowanym wyjątkiem nieodczytywanych bajtów $0270–$0277.

Lot prosto: joystick neutralny przez cały test. Sterowanie: neutralna rozgrzewka, następnie od początku pomiaru powtarzany cykl 1 s joystick w górę (nurkowanie), 3 s neutralnie; bez skrętów i strzelania. Terminy sterowania zależą od taktów Atari, nie liczby obrazów ani zegara komputera.

Licznik prezentacji: B516; liczone pełne odstępy między gotowymi obrazami. Pierwszy pełny odstęp po 60 s domyka okno. Wcześniejsze naturalne zakończenia lotu pozostają w zbiorze, z czasem do ostatniego gotowego obrazu przed końcem. Żadnych odrzuconych skrajnych wyników. Główna średnia nadaje każdemu lotowi jednakową wagę; kontrolnie podano wynik ważony czasem.

WYNIKI

PAL
prosto: up38 8.936562 FPS; candidate 9.077906 FPS; delta +0.141345 FPS; gain +1.5816%.
Przedział 95% dla różnicy FPS: [+0.095330, +0.189203]; dla zysku: [+1.0637%, +2.1236%].
  up38: SD=0.531235; median=8.890032; mean CI95=[8.864113, 9.009909]; early ends=3/155; seconds=[24.889, 60.127]; pooled FPS=8.946967.
  candidate: SD=0.525716; median=9.048928; mean CI95=[9.006947, 9.148909]; early ends=5/155; seconds=[26.935, 60.168]; pooled FPS=9.088176.
sterowanie: up38 8.086260 FPS; candidate 8.487950 FPS; delta +0.401690 FPS; gain +4.9676%.
Przedział 95% dla różnicy FPS: [+0.369812, +0.433109]; dla zysku: [+4.5688%, +5.3620%].
  up38: SD=0.446394; median=8.140872; mean CI95=[8.026410, 8.144654]; early ends=6/155; seconds=[41.917, 60.168]; pooled FPS=8.089162.
  candidate: SD=0.480476; median=8.476662; mean CI95=[8.422715, 8.552225]; early ends=3/155; seconds=[29.723, 60.127]; pooled FPS=8.490533.
Dodatkowy zysk względny przy sterowaniu względem lotu prosto: +3.3859 p.p.; CI95=[+2.7171, +4.0260].
Dodatkowy zysk bezwzględny FPS: +0.260346; CI95=[+0.202767, +0.315505].
W tym teście sterowanie zwiększyło względną przewagę kandydata; przedział nie obejmuje zera.

NTSC
prosto: up38 8.167030 FPS; candidate 8.312030 FPS; delta +0.145000 FPS; gain +1.7754%.
Przedział 95% dla różnicy FPS: [+0.097869, +0.191921]; dla zysku: [+1.1935%, +2.3582%].
  up38: SD=0.517654; median=8.075168; mean CI95=[8.093205, 8.241723]; early ends=0/155; seconds=[60.011, 60.144]; pooled FPS=8.166987.
  candidate: SD=0.504864; median=8.203808; mean CI95=[8.242746, 8.381982]; early ends=2/155; seconds=[51.199, 60.161]; pooled FPS=8.313216.
sterowanie: up38 7.309115 FPS; candidate 7.694186 FPS; delta +0.385071 FPS; gain +5.2684%.
Przedział 95% dla różnicy FPS: [+0.359168, +0.411162]; dla zysku: [+4.9142%, +5.6275%].
  up38: SD=0.361053; median=7.321857; mean CI95=[7.257190, 7.361106]; early ends=10/155; seconds=[44.374, 60.311]; pooled FPS=7.311214.
  candidate: SD=0.408361; median=7.752359; mean CI95=[7.634656, 7.752224]; early ends=5/155; seconds=[48.446, 60.144]; pooled FPS=7.698062.
Dodatkowy zysk względny przy sterowaniu względem lotu prosto: +3.4929 p.p.; CI95=[+2.8247, +4.1513].
Dodatkowy zysk bezwzględny FPS: +0.240071; CI95=[+0.187409, +0.292126].
W tym teście sterowanie zwiększyło względną przewagę kandydata; przedział nie obejmuje zera.

Uwaga o wykonaniu: po zmianie transportu stary proces sterujący nie zakończył się z powodu błędnego filtra nazwy procesu. Przez część serii równolegle działały dwa zestawy po cztery emulatory, dublujące niektóre obliczenia. Stary proces i jego dzieci zostały zidentyfikowane i zatrzymane. Do analizy wchodzi dokładnie jeden zapis na konfigurację/standard/numer próby. Szczegóły: runtime_notes.json. To zmieniało obciążenie hosta, nie liczbę taktów Atari; zgodność sprawdzają kontrole odtwarzalności.

NIEPEWNOŚĆ I INTERPRETACJA
50 000 replikacji bootstrapu całych sparowanych lotów wewnątrz 31 bloków; seed 2026103001. Wszystkie cztery konfiguracje zachowują wspólne indeksy losowania. Przedziały percentylowe 95%, bez korekty na skończoną populację 600 momentów START i bez korekty wielokrotnych porównań. Są przybliżone i dotyczą tego harmonogramu oraz określonego sposobu lotu, nie całej gry. Punkty 15/30/60 s są zależnymi oknami tych samych lotów.

Wspólne wejście i harmonogram sterowania nie gwarantują identycznej późniejszej geometrii, zdarzeń ani chwili końca lotu w wersjach o różnym czasie wykonania. Nurkowanie zmienia nie tylko ilość widocznego nieba. Test ocenia praktyczny FPS ustalonego scenariusza, nie izoluje przyczynowo samego udziału gór w obrazie. Różną częstość wcześniejszych końców trzeba uwzględnić przy interpretacji średnich; nie wykluczaliśmy takich lotów po obejrzeniu wyników.

WALIDACJA I PRZYSPIESZENIE
TCP_NODELAY włączone. Polecenia kroku, odczytu PC/trybu i zegara są przesyłane wspólnie, z zachowaniem kolejności i barier emulatora. Osiem kontroli dało identyczne zdarzenia, terminy joysticka i końcowy RAM jak zwykły transport. Cztery kontrole lotu prosto zgadzały się ze starym licznikiem; cztery kontrole sterowania sekwencyjnego zgadzały się z równoległym. Po zmianie transportu zachowano ukończone wyniki, a przerwane loty uruchomiono ponownie od początku. Alternatywny licznik profilera odrzucono z powodu limitu 4096 rekordów; nie wniósł żadnych wyników do serii.

Historical up38 straight-flight FPS/count exact matches: 310/310. Maximum input timing rounding: 0.5 Atari ticks.

PLIKI
plan.json; validation.json; transport-validation.json; integrity.json; summary.json; entry-equivalence.json; entry-diagnostic/read-watch.json; entry-diagnostic/read-watch-steering.json; benchmark.json; main/*.json; FPS_GAIN.png/svg; FPS_DISTRIBUTION_PAL.png/svg; FPS_DISTRIBUTION_NTSC.png/svg; ALL_FLIGHTS_PAL.png; ALL_FLIGHTS_NTSC.png.
scripts/benchmark_up38_full.py; scripts/summarize_up38_full.py; scripts/report_up38_full.py.

Wersje ROM nie zostały zmodyfikowane ani opublikowane w ramach tego pomiaru.

Końcowe kontrole: wszystkie 310 lotów up38 na wprost odtworzyło historyczne FPS i liczby prezentacji. Cztery niezależne powtórki kandydata (PAL/NTSC, prosto/sterowanie) dały identyczne znaczniki wszystkich prezentacji, wyniki, sterowanie oraz pełny RAM na wejściu i końcu. Dane: post-validation.json. Osiem grup startów miało różne surowe skróty RAM; porównania offline wykazały różnice wyłącznie pod $0270–$0277 (0 albo 228). Osiem dodatkowych 60-sekundowych obserwacji odczytów, obejmujących obie wersje i oba sposoby lotu dla prób PAL 11 i 13, nie wykazało odczytu tych bajtów. Pamięci pomiarowych lotów nie modyfikowano.



Powyższe nazwy lokalnych plików dotyczą archiwum badania. Publikowane obserwacje połączono w results/v11/flights.jsonl; plany, walidację i podsumowania zapisano obok. Zrzutów RAM nie publikujemy.
