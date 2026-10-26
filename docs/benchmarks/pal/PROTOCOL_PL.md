# PAL: powtórzenie automatycznego testu NTSC

[English](PROTOCOL.md) · [Polski](PROTOCOL_PL.md)

Plan zapisano przed pomiarami. Liczba prób: 155 na wersję, 310 łącznie, bez dobierania liczebności po obejrzeniu wyników. Scenariusze i kolejność są kopią harmonogramu głównego badania NTSC. Nie wykonujemy pilota do planowania nowej liczebności PAL.

Każda próba: nowy proces AltirraBridgeServer, standardowy Atari 800XL 64 KB PAL, natywny BOOT oryginału lub v9, START po zapisanej liczbie ramek menu (3000–3599), pierwsze wejście $A32E, zwolnienie START, 170 ramek rozgrzewki. Joystick przez cały czas wycentrowany, bez strzelania i dopalacza. Nie badamy skrętów ani nurkowania w doliny.

Mierzymy odstępy na $B516 przy aktywnym trybie lotu 2, używając zegara PAL 3546895/2 = 1773447,5 Hz. Ramka PAL: 114 × 312 = 35568 taktów. Limity 15/30/60 sekund kończą się na pierwszym pełnym odstępie przekraczającym limit. Są to zagnieżdżone okna jednej próby. Czas wykonania na komputerze nie wchodzi do FPS.

Od początku obowiązuje reguła: jeśli gra wcześniej opuści tryb lotu, zachowujemy próbę i wynik do ostatniego pełnego odstępu lotu. Nie doliczamy sekwencji zakończenia gry i nie zastępujemy scenariusza innym. Brak mierzalnego odstępu lub inne niespodziewane zatrzymanie jest błędem wymagającym diagnozy, nie podstawą do cichego usunięcia próby.

Zachowano liczbę ramek oczekiwania i rozgrzewki, a nie ich czas rzeczywisty: 170 ramek to około 3,41 s PAL wobec 2,84 s NTSC. Główny limit lotu w obu standardach wynosi 60 sekund. Nie zakładamy jednakowych map dla PAL, NTSC, oryginału i v9.

Przed główną serią zwalidowano cztery scenariusze PAL po 15 s (dwa na wersję), każdy sekwencyjnie i równolegle. Wyniki odstępów między obrazami oraz RAM przy wejściu, po rozgrzewce i na końcu są dokładnie zgodne. Dane: ../pal_parallel_validation/validation.json. Loty walidacyjne nie powiększają próby głównej.

Wykonanie: maksymalnie cztery odizolowane procesy, każdy z własnym portem, tokenem, kontrolerem i plikami. Zrównoważone bloki po pięć lotów każdej wersji; kolejny blok po zakończeniu poprzedniego. Jeden wątek zapisuje agregat w kolejności harmonogramu przez atomową podmianę pliku.

Główna statystyka to średnia arytmetyczna FPS poszczególnych lotów, iloraz średnich v9/original oraz przybliżony przedział ufności 95%. Kontrolnie: bootstrap całych lotów wewnątrz blok/wariant i wynik ważony czasem. Bez odrzucania skrajnych wyników. Przedział dotyczy zdefiniowanego zbioru scenariuszy, nie wszystkich sposobów grania.

Po zakończeniu: kontrola zgodności z planem, hashy i ponowne przeliczenie liczników; raport po polsku, analogiczne wykresy po angielsku w PNG oraz SVG. Pliki gier i ich nazwy pozostają niezmienione.
