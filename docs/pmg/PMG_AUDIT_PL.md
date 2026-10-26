Dokument badawczy zachowany historycznie. Dawne ścieżki i wyniki dotyczą opisanego eksperymentu; aktualną implementację opisuje docs/OPTIMIZATIONS_PL.md, a wyniki zbiorcze docs/benchmarks/METHOD_PL.md (ścieżki od katalogu głównego repozytorium).

[English](PMG_AUDIT.md) · [Polski](PMG_AUDIT_PL.md)

# Audyt procedur PMG w v8

21.10.2026. Badanie kodu, liczby zapisów i organizacji pętli. Bez zmian gry,
bez nowego wydania i bez szacowania wpływu na FPS.

ROM v8: `02da0221c95fc8896720a7ca17181bbb1c3c7502dadf62d933d1ba0c341347bd`.

## Zakres i metoda

Przejrzano kod stałego banku ROM oraz kod RAM z zachowanego stanu lotu.
Wybrane procedury ROM porównano bajtowo z oryginałem: są identyczne.
Listing od znanych punktów wejścia: `PMG_ROUTINES_PL.txt`.
Pełne liniowe disasemblowanie jest tylko narzędziem wyszukiwania:
w tablicach danych może pokazywać pozorne instrukcje i nie dowodzi użycia kodu.

W emulatorze v8 zebrano po 8 rzeczywistych wejść do $A527, $A55C, $A94D
i $A8DE. Wejścia odtworzono w modelu CPU, licząc zapisy i instrukcje.
To próbki wejść, nie profil częstości ani pomiar czasu całej rozgrywki.
$A71E osiągnięto również w zachowanych stanach wyższych poziomów, ale
z argumentem $7F i pustym poprzednim rysunkiem. Aktywnego $710D nie
osiągnięto w badanych oknach; tę procedurę sprawdzono statycznie i na
kontrolowanym wejściu syntetycznym. Nie deklarujemy pełnego testu wszystkich
animacji, faz ratowania pilota ani spotkania z obcym.

Wyniki: `live-input-observations.json`, `special-paths.json`,
`cpu-observations.json`. Cykle w ostatnim pliku są cyklami CPU bez DMA
i przerwań. Odtwarzanie rejestrów sprzętu jako stałych wartości nie odtwarza
dokładnie losowego POKEY RANDOM. Surowe stany pamięci są materiałem lokalnym.

## Mapa pamięci i harmonogram

Emulator potwierdził PMBASE=$08 i DMACTL=$3F. Pamięć pocisków jest pod
$0B00–$0BFF, graczy P0/P1/P2/P3 pod $0C00/$0D00/$0E00/$0F00.
$0800–$0AFF nie należy w tym trybie automatycznie traktować jako obrazu PMG:
gra przechowuje tam także dane innych mechanizmów.

PMG obsługuje również kokpit, a nie tylko obiekty na tle gór. Gra używa
tych samych graczy na różnych wysokościach ekranu, zmieniając rejestry
GTIA w DLI. Zapisy położeń, szerokości i kolorów w $AE96..$AF41 oraz VBI
nie są zwykłym redundantnym powtarzaniem stałych. Usuwanie ich wymaga
uwzględnienia innych części obrazu i momentu działania DLI.

$A527, $A55C i $A94D są wywoływane w gałęzi VBI pod $B68E..$B69A.
Licznik $0640 rozdziela pracę na dwie gałęzie, ustawiając wartość 2 w $B5C0.
Nie należy zakładać, że każdy renderer wykonuje się przy każdej nowej
klatce terenu ani że wszystkie działają w każdym VBI.

## Procedury i ustalenia

| Adres | Działanie | Ocena |
|---|---|---|
| $A527–$A55A | Wybór wzoru i zapis 21 wierszy P2 oraz dwóch bajtów brzegowych | Porównuje $291C/$291D z zapamiętanymi $2872/$2874. Gdy nie ma zmian, zero zapisów. Pętla stała, 21 powtórzeń, licznik DEC $BD. |
| $A55C–$A57B | Pasek P0 w $0C97–$0CCF | Pomija brak zmiany, ale każda zmiana powoduje 57 zapisów: zerowanie jednej części i wypełnienie drugiej $FF. Najbardziej oczywista nadmiarowa praca. |
| $A57C–$A5A6 | Dwuwierszowy znacznik M3 | Tylko po zmianie. Dwa AND #$3F i dwa ORA #$C0. Zachowuje bity innych pocisków. Kod już rozwinięty. |
| $A632/$A65B/$A65F | Pasek P1, zakres od $0D98 | Aktualizacja granicy pojedynczym zapisem; nie przepisuje pełnego paska. Nie ma podstaw do analogicznego zarzutu jak przy $A55C. |
| $A71E–$A83D | Obiekt P3, obszary $0F1E+X i $0F71+X | Pamięta początek $286F i długość $2835. Kasuje poprzedni zakres, wybiera kształt i przycina oba obszary. Wiersze używają maski $2826 lub odczytu RANDOM. |
| $A8DE–$A93D | Pięciowierszowy obiekt/znacznik P3 przy $0F98+Y | Pomija niezmienioną pozycję. Po zmianie kasuje 5 bajtów, a gdy aktywny rysuje 5 nowych; trzy warianty wzoru. |
| $A94D–$A993 | Trzywierszowy znacznik M2 | Porównuje starą i nową pozycję. Kasuje 3 bajty przez AND #$CF i ustawia 3 przez ORA #$30, zachowując pozostałe pociski. |
| $710D–$7269, RAM | Obiekt P2: kasowanie, pozycja, wzór i powtarzanie wierszy | Kasuje tylko poprzednią długość $2866 od pozycji $2865. Kasowanie używa DEC $BD; pionowe powtarzanie wierszy DEC $BE. Wyboru skali i faz animacji nie wolno pominąć. |
| $4FC2–$5013, RAM | Przesunięcie czterech płaszczyzn P0–P3 o wiersz i dodanie nowego | 89 iteracji, każda kopiuje 4 bajty, następnie dodawane są 4 bajty. 356 zapisów przesunięcia + 4 nowego wiersza. Ścieżka sterowana przez $89 i dyspozytor $B7EE; nie przypisano jej kosztu do zwykłego lotu. |
| $AA65–$AA7C | Inicjalizacja trzech zakresów po 8 bajtów | Kopie stałych tablic do P0, P1 i pocisków. Nie jest główną pętlą lotu. |

Inicjalizacja $A02A ustawia zakres $0B00–$0FFF i używa uniwersalnego
wypełniania $A0A1. To 1280 bajtów; procedura aktualizuje 16-bitowy wskaźnik
i licznik dla każdego bajtu. Jest potencjał specjalizacji, ale jest to
inicjalizacja, nie czyszczenie całej pamięci PMG co ramkę. Dodatkowe pętle
$443F, $45A0/$45BB, $4D52, $4EE6, $5018, $588E, $58B3, $58CE oraz
$A3FD/$A405 obsługują przygotowanie/zmiany obrazów i wybrane zakresy PMG.
Nie zaliczono ich automatycznie do stałego kosztu lotu.

## Konkretne możliwości, bez implementacji i bez prognozy FPS

### 1. Aktualizacja różnicowa paska $A55C

Dla prawidłowego poprzedniego obrazu przesunięcie 20→21 lub 21→20
zmienia dokładnie 1 bajt, ale oryginał wykonuje 57 zapisów. Potwierdzono
to wykonaniem oryginalnego kodu: 56 zapisów odtwarza tę samą wartość.
Można zapisywać tylko przedział między starą i nową granicą; przy zmianie
o d kroków będzie to |d| bajtów zamiast 57. Brak zmiany już dziś nic nie zapisuje.

Warunek: stara wartość $2875 musi odpowiadać faktycznej zawartości PMG.
Inicjalizacja, restart i przejścia ekranów muszą ustanawiać ten warunek
albo wymuszać jednorazowe pełne odrysowanie. Nie wystarczy podmienić pętli
bez analizy pozostałych autorów zapisów do tego zakresu.

### 2. Rozwinięcie krótkich pętli o stałej długości

Najbardziej czytelne miejsca: 21-wierszowa kopia $A54A, 5-wierszowe
kasowanie i kopiowanie $A8EA/$A91E, dwie pętle po 3 wiersze $A965/$A975.
Można usunąć część liczników i skoków, zachowując maski oraz końcowy
stan rejestrów, flag i pamięci roboczej. W $A91E licznik jest w ZP ($BB),
chociaż rozmiar zawsze wynosi 5. To konkretna możliwość uproszczenia
niskopoziomowego, niezależna od zmiany logiki gry.

### 3. Liczniki i specjalizacja renderera RAM $710D

Pętla kasowania $7119: STA abs,Y / INY / DEC zp / BNE.
DEC zp kosztuje więcej niż dekrementacja rejestru. X jest jednak żywym
argumentem, zapisywanym dopiero w $712A, więc użycie X wymaga wcześniejszego
zachowania i poprawnego przywrócenia. Nie jest bezwarunkową zamianą jednej
instrukcji na drugą. Rozwinięcie bloków kasowania ogranicza liczbę skoków.

Pętla $71D5 sprawdza granicę X<$56 przy każdym powtórzeniu tego samego
wiersza i odlicza $BE. Można rozważyć osobne ścieżki dla wnętrza ekranu,
brzegu i częstych małych współczynników powtarzania. Trzeba zachować także
to, że po osiągnięciu granicy X już nie rośnie.

Ponieważ kod jest w RAM, dopuszczalne są samomodyfikujące operandy
adresów/końca pętli. Ich przygotowanie ma koszt; nie ma podstaw zakładać,
że SMC zawsze będzie lepsze. Procedura działa w kontekście przerwania,
więc DLI i współdzielone operandy muszą pozostać bezpieczne.

### 4. Rozdzielenie ścieżek obiektu P3 $A71E

W pętli rysującej $A7F3 każdorazowo odczytywane i testowane jest $2826.
Osobne ścieżki maska stała / RANDOM mogłyby ograniczyć narzut tego wyboru.
W ścieżce RANDOM trzeba zachować odczyt sprzętu dla każdego wiersza.
Przyspieszenie zmieni moment odczytu RANDOM, więc sama liczba odczytów
nie daje identycznego losowego przebiegu względem oryginału.

Kasowanie $A77B sprawdza próg Y<$4F w każdej iteracji. Można podzielić
zakres na odcinki przed i po progu. Rysowanie również ma kilka progów
X ($14/$2E/$4F/$73). Specjalizacja wymaga zachowania dokładnej kolejności
zużywania danych źródłowych, terminatorów oraz indeksów — nie wystarczy
wyciąć wszystkie testy dla jednego przykładu.

### 5. Przewijanie PMG w RAM $4FC4

Kod jest już rozwinięty na cztery kanały, ale ma wspólną pętlę 89 wierszy.
Możliwe jest częściowe lub pełne rozwinięcie: mniej INY/CPY/BNE oraz
stałe adresy zamiast abs,Y. Sam fakt, że kod jest w RAM, nie wymusza SMC:
adresy tego przesunięcia są stałe. Pełne rozwinięcie wymaga znacznie
więcej miejsca i osobnej decyzji o lokalizacji kodu.

Kopiowanie jest nakładające się i przebiega od niższych do wyższych adresów,
ze źródła o jeden bajt wyżej. Nie wolno odwrócić kierunku. Nowy wiersz
jest generowany z RANDOM, więc jego semantyka pozostaje osobnym warunkiem.

## Wnioski

PMG nie było potraktowane naiwnie w całej grze: istnieją pamięć starego
zakresu, pomijanie niezmienionych danych i małe aktualizacje granic.
Najmocniej potwierdzona nadmiarowa praca to pełne odrysowanie paska $A55C.
Najczytelniejsze możliwości stricte asemblerowe to stałe pętle 3/5/21
wierszy oraz liczniki i powtarzanie wierszy renderera RAM.

Nie zmieniono żadnego ROM-u, nie wygenerowano nowego wydania i nie
oszacowano wpływu na FPS. Nie wykazano też, że każda z tych opcji jest
opłacalna po uwzględnieniu kodu integracji. Następny etap, jeśli zostanie
podjęty, powinien zacząć się od kontraktów pamięci i testów porównawczych,
a nie od automatycznego wdrożenia wszystkich propozycji.
