from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/ntsc_comparison'
b=json.loads((OUT/'benchmark.json').read_text());rows=b['rows'];fps={}
for variant in ('original','v9'):
 rr=[r for r in rows if r['variant']==variant];assert len(rr)==4 and all(r['mode']==2 for r in rr)
 fps[variant]=sum(r['intervals'] for r in rr)*b['clock_hz']/sum(r['ticks'] for r in rr)
gain=100*(fps['v9']/fps['original']-1)
summary={'result':'pass','video':'ntsc','fps':fps,'gain_fps':fps['v9']-fps['original'],'gain_percent':gain,'original_sha256':b['original_sha256'],'v9_sha256':b['v9_sha256'],'common_initial_state':True,'clock_hz':b['clock_hz'],'minimum_frames_per_scenario':b['minimum_frames'],'rows':rows,'limitations':'One paired set of four scenarios, same initial game state but trajectories can diverge as performance changes. No confidence interval or physical hardware tests.'}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2))
labels={'straight':'Prosto','right':'Skręt w prawo','left':'Skręt w lewo','fast_right':'Szybki lot w prawo'};table=[]
for s in labels:
 a=next(r['fps'] for r in rows if r['variant']=='original' and r['scenario']==s);v=next(r['fps'] for r in rows if r['variant']=='v9' and r['scenario']==s)
 table.append(f'| {labels[s]} | {a:.6f} | {v:.6f} | {100*(v/a-1):+.3f}% |')
report=f'''# NTSC — porównanie oryginału i v9

22.10.2026. Atari 800XL, 64 KiB RAM, NTSC, bez przyspieszaczy.

**Oryginał: {fps['original']:.6f} FPS. V9: {fps['v9']:.6f} FPS.**
**Wzrost: {fps['v9']-fps['original']:+.6f} FPS, czyli {gain:+.3f}%.**

| Scenariusz | Oryginał | v9 | Zmiana |
|---|---:|---:|---:|
{chr(10).join(table)}

Wynik łączny jest sumą odstępów między prezentacjami podzieloną przez
sumę czasu emulowanego dla danej wersji. Nie jest średnią arytmetyczną FPS.
Każdy z ośmiu pomiarów trwa co najmniej 3600 ramek NTSC, około minuty.
Liczone są nowe obrazy prezentowane przy $B516, a nie ramki odświeżania.
Wszystkie próby pozostawały w trybie lotu przy każdej prezentacji.

## Wspólne warunki początkowe

Oryginał uruchomiono od zimnego startu w NTSC i zatrzymano przy pierwszym
wejściu do głównej pętli lotu $A32E, w banku 2. Zapisano ten sam stan
emulatora dla obu wersji. Jest to granica przed obliczeniami geometrii,
bez aktywnej procedury optymalizowanego renderera na stosie.

Przed każdą próbą ładowano właściwy cartridge, wspólny stan, a następnie
sprawdzano konfigurację NTSC/64 KiB, PC i bank oraz cały widoczny bank 2
i stały bank ROM. Oryginał wykonywał swój oryginalny kod RAM. Wyłącznie
dla v9 podmieniono udokumentowane 215 bajtów kodu RAM $7EEB..$7FC1 na
kod v9, potrzebny do jej działania. Przed wykonaniem sprawdzano całe
32 KiB RAM: identyczne między wersjami poza tym celowym fragmentem kodu.

Następnie obie wersje wykonywały 120 ramek lotu bez wychylenia joysticka,
po czym ustawiano kierunek scenariusza i wykonywano 50 ramek rozgrzewki.
W szybkim locie przed rozgrzewką dodatkowo przytrzymywano OPTION przez
45 ramek. Zegar NTSC: 1789772,5 Hz, ramka: 29868 taktów (114*262).
Po każdym przebiegu sprawdzano sygnaturę właściwego kodu RAM.

Szybszy kod zmienia postęp gry w czasie, więc nie gwarantuje identycznej
geometrii w każdej kolejnej klatce obu przebiegów. To porównanie wspólnego
stanu wejściowego i protokołu sterowania, nie test samych cykli renderera
na zamrożonym zestawie scen. Jedna seria nie daje przedziału ufności.

## Relacja do wcześniejszego pomiaru v9

Wcześniejsze 6,810914 FPS pochodziło z osobnego zimnego startu v9.
Do tego porównania zmierzono v9 ponownie ze wspólnego stanu oryginału.
Procentowy zysk powyżej używa wyłącznie tej nowej pary pomiarów.
Nie należy łączyć licznika z jednej serii z mianownikiem z drugiej.
Historyczny raport POMIAR_NTSC_V9_PL.md pozostaje zapisem poprzedniego testu.

Oryginał może wykazywać wcześniej zidentyfikowany wyścig buforów; licznik
prezentacji nie oznacza, że każda wyświetlona ramka była bez artefaktów.
V9 zawiera naprawę synchronizacji i optymalizację PMG.

## Pliki i odtworzenie

Oryginał SHA256: `{b['original_sha256']}`.
V9 SHA256: `{b['v9_sha256']}`.
Nie zmieniono ROM-ów, nazw istniejących plików ani README.

Skrypty: `python scripts/compare_ntsc.py prepare`, następnie
`python scripts/compare_ntsc.py benchmark` i `python scripts/report_ntsc_comparison.py`.
Wymagają lokalnego mostka Altirry i SDK. Przygotowanie tworzy świeży stan
z oryginału, więc nie wymaga dawnych stanów PAL ani poprzednich dumpów.
Dokładne ponowienie tej samej sesji wymaga zachowanego lokalnego stanu;
nowy zimny start może dać inny przebieg losowy i trochę inne wyniki.
W kopii repozytorium oryginał jest w original/Rescue on Fractalus!.rom;
skrypt obsługuje również pierwotne lokalne położenie w katalogu projektu.

Zwarte wyniki i konfiguracja są w results/ntsc_comparison. Screeny, stany
i surowe znaczniki prezentacji pozostają lokalnie, poza repozytorium.
'''
(OUT/'POROWNANIE_NTSC_PL.md').write_text(report,encoding='utf-8');print(json.dumps({'fps':fps,'gain_percent':gain},indent=2))
