from ntsc_v9_common import *
b=json.loads((OUT/'benchmark.json').read_text());rows=b['rows'];assert len(rows)==4
for name in ('preparation','stress','validation'):
 d=json.loads((OUT/f'{name}.json').read_text());assert d['result']=='pass' and d['rom_sha256']==SHA
visual=json.loads((OUT/'visual-controls.json').read_text());assert visual['rom_sha256']==SHA
count=sum(r['intervals'] for r in rows);ticks=sum(r['ticks'] for r in rows);fps=count*FREQ/ticks
summary={'result':'pass_with_stated_scope','version':'v9','rom_sha256':SHA,'video':'ntsc','clock_hz':FREQ,'frame_ticks':FRAME_TICKS,'fps':fps,'presentation_intervals':count,'ticks':ticks,'seconds':ticks/FREQ,'scenarios':[{k:r[k] for k in ('scenario','intervals','ticks','seconds','fps','mode_throughout')} for r in rows],'pmg_checks':240,'safe_clear_checks':120,'original_or_other_versions_tested':False,'note':'Fresh NTSC states; not a controlled PAL/NTSC performance comparison. No physical hardware or exhaustive gameplay/audio verification.'}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2))
labels={'straight':'Prosto','right':'Skręt w prawo','left':'Skręt w lewo','fast_right':'Szybki lot w prawo'}
table='\n'.join(f"| {labels[r['scenario']]} | {r['intervals']} | {r['seconds']:.3f} | {r['fps']:.6f} |" for r in rows)
report=f'''# V9 — pomiar FPS i kontrola działania w NTSC

22.10.2026. Testowano wyłącznie istniejące wydanie v9. Nie modyfikowano ROM-u
ani nazw plików. Nie badano oryginału i innych wersji.

**Średni wynik zestawu: {fps:.6f} FPS.**

| Scenariusz | Odstępy między prezentacjami | Czas emulowany [s] | FPS |
|---|---:|---:|---:|
{table}

Łącznie {count} odstępów między nowymi obrazami w {ticks/FREQ:.6f} s.
Wynik to suma odstępów / suma czasu, nie średnia arytmetyczna czterech FPS.

## Konfiguracja i metoda

Altirra headless, 800XL, 64 KiB RAM, NTSC, bez Rapidusa, VBXE i U1MB.
Plik: `dist/Rescue on Fractalus! - PAL optimized v9 128KB.car`.
ROM SHA256: `{SHA}`.

Zegar NTSC: 3579545/2 = 1789772,5 Hz. Ramka: 114*262 = 29868 taktów.
Stałe zgodne z lokalnym źródłem Altirry (analysis/altirra-constants.h).
Sprawdzono empirycznie: 120 ramek daje dokładnie 3584160 taktów.
Konfigurację NTSC i 64 KiB potwierdzano również po wczytaniu każdego stanu.

Wczytanie dawnych stanów PAL przywraca PAL; przełączenie konfiguracji na
NTSC resetuje emulowaną maszynę. Z tego powodu wszystkie nowe stany
przygotowano od zimnego startu v9 w NTSC. Nie podmieniano kodu RAM z dawnych
stanów. Zgodność zainicjalizowanego kodu RAM v9 sprawdzano z pominięciem
ośmiu celowo samomodyfikowanych operandów interpolacji.

Cztery loty zaczynają z tego samego świeżego stanu NTSC. Stan zapisano
120 ramek po pierwszym wejściu do głównej pętli lotu $A32E. Przed pomiarem
jest 50 ramek rozgrzewki, a wariant szybki dodatkowo przytrzymuje OPTION
przez 45 ramek. Każdy pomiar obejmuje co najmniej 3600 ramek NTSC (~60 s).
Liczone są kolejne wykonania $B516, czyli prezentacje nowych buforów,
a nie każda ramka odświeżania. Wszystkie próby FPS pozostawały w trybie
lotu ($4A=2) przy każdej zarejestrowanej prezentacji.

To nowy zestaw wejść. Wyniku nie należy bezpośrednio zestawiać procentowo
z dawnymi 7,764418 FPS dla PAL: różnią się stany i przebieg lotów.
Nie określono procentowego zysku względem oryginalnej gry w NTSC,
ponieważ zgodnie z prośbą użytkownika nie testowano oryginału.

## Kontrola działania

- Zimny start, ekran tytułowy, rozpoczęcie lotu i ponowny zimny start.
- Dodatkowe stany utworzone po 7 i 15 impulsach SELECT (12 ramek
  przytrzymania i 12 zwolnienia). To nazwy sekwencji wyboru, nie numery
  poziomów. Po trzy próby lotu po 3600 ramek dla każdego stanu.
  Trzy próby stanu select7 kończą się trybem 0; przejrzany obraz pokazuje
  tabelę wyników. Nie są zaliczone do pomiaru FPS ani opisane jako
  nieprzerwany lot. Próby select15 kończą się w trybie 2.
- START z banków 5,6,8,9,10,11,12,13,14: wszystkie próby wróciły do lotu.
  W bankach geometrii cztery orientacje wymuszono jako jawne wejście
  testowe, aby sprawdzić każdy bank. Pozostałe próby nie zmieniały danych gry.
- 240 wejść PMG: po 80 dla trzech stanów, zgodna zawartość paska i jego
  zapamiętana granica; obsługa działała w banku 2.
- 120 wejść do właściwego czyszczenia obrazu: po 40 dla trzech stanów,
  zawsze po potwierdzeniu przełączenia bufora przez VBI ($42=0).
- START podczas oczekiwania na zwolnienie bufora: powrót do lotu.
- Cztery próby sterowania góra/dół/lewo/prawo ze wciśniętym FIRE, po
  1200 ramek; sprawdzono dalsze działanie emulatora i sygnaturę kodu RAM.
  Same te testy nie stanowią dowodu pełnej poprawności trafień/kolizji.
- Zapis obrazu przez 1200 kolejnych ramek NTSC, wybrane obrazy i zmiany
  po lewej do kontroli wizualnej. Detektor zgłasza także prawidłowe zmiany
  terenu i obiektów; nie jest automatycznym dowodem braku wszelkich gliczy.

Przejrzane obrazy lotu i kokpitu nie pokazały odpowiednika naprawionego
klina ani widocznego uszkodzenia PMG. Głównym sprawdzeniem dawnego wyścigu
jest kontrola $42 przed czyszczeniem, a nie pojedynczy końcowy screen.

## Wniosek i granice

V9 działa poprawnie w wykonanym zestawie testów NTSC. Nie znaleziono
potrzeby tworzenia osobnego ROM-u NTSC. Nie jest to dowód poprawności
każdej fazy i każdego poziomu gry: nie wykonano pełnego przejścia,
porównania dźwięku próbka w próbkę ani testów na fizycznym Atari.
Pomiar FPS jest jedną serią czterech scenariuszy, bez przedziału ufności.

## Odtworzenie badania

Kolejność skryptów: prepare_ntsc_v9.py, benchmark_ntsc_v9.py,
stress_ntsc_v9.py, validate_ntsc_v9.py, visual_ntsc_v9.py,
report_ntsc_v9.py. Wymagają działającego lokalnego mostka Altirry
i jego SDK. Skrypt przygotowania tworzy świeże stany NTSC — nie wymaga
dawnych stanów PAL. Nie uruchamiać kilku skryptów równocześnie na jednym
emulatorze. Narzędzia i stany pozostają poza kopią repozytorium.

Zwarte wyniki w results/ntsc_v9/*.json. Screeny, surowe znaczniki czasu
i stany testowe pozostają lokalnie. Nazwy istniejących plików nie zmienione.
'''
(OUT/'POMIAR_NTSC_V9_PL.md').write_text(report,encoding='utf-8');print(json.dumps(summary,indent=2))
