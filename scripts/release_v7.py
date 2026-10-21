import pathlib,json,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'results/research_v6';dist=ROOT/'dist';sha=lambda d:hashlib.sha256(d).hexdigest()
rom=(ROOT/'build/v7_clipping.rom').read_bytes();stress=json.loads((OUT/'stress.json').read_text());assert stress['result']=='pass' and stress['rom_sha256']==sha(rom)
for path in ('results/opt14/v7-geometry-tests.json','results/research_v6/clipping-tests.json','results/research_v6/integration-tests.json','results/research_v6/geometry-live-probe.json'):assert json.loads((ROOT/path).read_text())['result']=='pass'
variants=['opt14_interpolation','v7_geometry','v7_clipping'];bench=[r for r in json.loads((ROOT/'results/opt14/benchmark.json').read_text()) if r['variant'] in variants];fps={}
for v in variants:
 rows=[r for r in bench if r['variant']==v];assert len(rows)==4 and all(r['mode']==2 for r in rows);fps[v]=sum(r['intervals'] for r in rows)*(3546895/2)/sum(r['ticks'] for r in rows)
assert fps[variants[1]]-fps[variants[0]]>=0.05 and fps[variants[2]]-fps[variants[1]]>=0.05
stem='Rescue on Fractalus! - PAL optimized v7 128KB';(dist/f'{stem}.rom').write_bytes(rom);(dist/f'{stem}.car').write_bytes((ROOT/'build/v7_clipping.car').read_bytes())
original=(ROOT/'Rescue on Fractalus!.rom').read_bytes();ips=bytearray(b'PATCH');pos=0
while pos<len(rom):
 if pos<len(original) and rom[pos]==original[pos]:pos+=1;continue
 start=pos
 while pos<len(rom) and (pos>=len(original) or rom[pos]!=original[pos]) and pos-start<65535:pos+=1
 ips+=start.to_bytes(3,'big')+(pos-start).to_bytes(2,'big')+rom[start:pos]
ips+=b'EOF';(dist/'fractalus-pal-optimized-v7-128KB.ips').write_bytes(ips)
stats={'result':'pass','fps':fps,'gain_vs_v6_percent':100*(fps[variants[2]]/fps[variants[0]]-1),'gain_vs_original_percent':100*(fps[variants[2]]/6.553531221-1),'scenarios':bench,'rom_sha256':sha(rom),'method':'sum presentations at B516 / sum emulated PAL time; four scenarios >=3000 frames each'}
(OUT/'final-summary.json').write_text(json.dumps(stats,indent=2));(OUT/'benchmark.json').write_text(json.dumps(bench,indent=2))
manifest={'sha256':sha(rom),'rom_bytes':len(rom),'cart_type':14,'original_sha256':sha(original),'performance':stats,'sources':{p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for pattern in ('src/v7_*.asm','scripts/build_v7_*.py','scripts/rebuild_v7.py') for p in ROOT.glob(pattern)}}
(dist/'build-manifest-v7.json').write_text(json.dumps(manifest,indent=2))
table='\n'.join(f'{v:24} {fps[v]:.6f}' for v in variants)
scenarios='\n'.join(f'{s:16} '+' '.join(f"{next(r['fps'] for r in bench if r['variant']==v and r['scenario']==s):.6f}" for v in variants) for s in ('straight','right','left','fast_right'))
report=f'''WYDANIE v7 — DALSZY AUDYT v6, PRÓG 0,05 FPS
21.10.2026, Atari XL/XE PAL, 64 KiB RAM, XEGS 128 KiB / CART 14.

WYNIK
{table}
Geometria: +{fps[variants[1]]-fps[variants[0]]:.6f} FPS.
Obcinanie, po geometrii: +{fps[variants[2]]-fps[variants[1]]:.6f} FPS.
Łącznie: +{fps[variants[2]]-fps[variants[0]]:.6f} FPS, +{stats['gain_vs_v6_percent']:.3f}% względem v6.
Względem oryginału 6,553531 FPS: +{stats['gain_vs_original_percent']:.3f}%.

Scenariusz       v6       geometria   v7
{scenarios}

Metoda jak poprzednio: suma prezentacji nowych obrazów przy $B516 / suma
czasu emulowanego, cztery loty po >=3000 klatek PAL, rozgrzewka 50 klatek.
To nie częstotliwość odświeżania PAL ani gwarancja tempa każdego lotu.
Baza v6 to zatwierdzony pomiar z poprzedniej sesji; nowe warianty mają ten
sam protokół i stan wejściowy. Szybszy kod zmienia przebieg lotu w czasie.
Nie wykonywano serii statystycznych powtórzeń ani pomiaru na fizycznym Atari.
Obcinanie nie przyspiesza każdego scenariusza: lot prosty zwalnia względem
samej nowej geometrii, ale pozostaje szybszy od v6.

ŚWIEŻY PROFIL v6
Po cztery pomiary callgraph i insns, każdy 3000 klatek PAL.
Góry: 35,13% czasu własnego; wypełnianie 9,40%; dzielenie 7,92%; pozostała
część terenu 7,17%; projekcja 5,43%; obcinanie 5,42%; czyszczenie 4,97%.
Ogon geometrii rozdziela się na banki 10..13; nie wolno przypisać całego
jego kosztu wyłącznie adresowi wejścia $8309.

1. SPECJALIZACJA OGONA GEOMETRII
Banki 10..13 nadal odpowiadają czterem niezmiennym strumieniom komend.
Dla punktów 0..32 rozwinięto również klasyfikację punktu i zastąpiono
adresowanie abs,Y stałymi adresami. Punkty 33..44 zachowują wspólną
klasyfikację, aby zmieścić kod i tabele w tych samych bankach 8 KiB.
Tablice $9D00 i $9E00 zastępują wysoką i niską część przesunięcia o 4 bity.
Niezmienny fragment zależny od $8B jest przygotowany raz na geometrię
w $9F. Stara wartość $9F jest odkładana na stos i przywracana przy wyjściu.
Odtworzono carry, znaki i zaokrąglenia; wynik końcowy A/X/Y/P/SP identyczny.
Bankowe wejście $9893 i wyjście $98E0 są zachowane; kod omija te miejsca.
Bez zwiększenia cartridge'a ani nowej rezerwacji RAM; jeden dodatkowy
bajt na istniejącym stosie sprzętowym przez czas geometrii.
58 scen: oszczędność 70336 cykli, średnio 1212,69 na geometrię.

Szacunek przed FPS: 0,0406..0,0610 FPS przy współczynniku wrażliwości
DMA 1..1,5; środkowy wariant 1,25 dawał 0,0508 FPS. Kandydat był blisko
progu, nie miał gwarantowanego minimum 0,05. Rzeczywisty pomiar dał +0,1162.
Rozbieżność jest powodem, by nie utożsamiać modelu CPU z końcowym FPS.

2. SZYBKA ŚCIEŻKA OBCINANIA
W 1938 wywołaniach z 58 scen 1533 miały X=0 i zerowe wysokie bajty
współrzędnych; 1521 dodatkowo zachowywało kolejność i zakres lewej strony.
905 można prowadzić bezpośrednio do rysowania, 283 pominąć, 333 wymagają
oryginalnego sprawdzenia mieszanego przypadku wysokości.
Nowy kod rozpoznaje ten przypadek i omija normalizację oraz redundantne
kontrole. Pozostałe dane idą oryginalną ścieżką. Nie zmieniono clippingu,
poziomu szczegółowości, rozdzielczości ani matematyki gór.
Wejście: bank2 $963D -> $8380, w obszarze nieużywanego już interpretera.
Powroty: oryginalne $972E/$974A/$9788/$9797; fallback odtwarza pierwszą
normalizację i wraca do $9648. Stan pomocniczy $9F/$B5 jest zachowany.
58 scen: oszczędność 105365 cykli, średnio 1816,64 na scenę.
Szacunek 0,061..0,092 FPS, środkowy 0,0763; zmierzono +0,0760 FPS.

ODRZUCONE / NIEPODJĘTE
- Łączenie diagonalnych kroków geometrii: tylko 16..20 powtórnych zapisów
  współrzędnych na 45 punktów. Budżet brutto 0,008..0,012 FPS, jeszcze
  przed przygotowaniem współczynników. Poniżej progu, bez implementacji.
- Osobny dzielnik dla D<256: historyczny ślad 6/2766 przypadków. Nawet
  250 cykli oszczędności na trafienie daje około 0,0013 FPS brutto przed
  kosztem rozpoznania. Nie zbierano dodatkowego śladu dla tego małego zysku.
- Prosta zamiana wskaźnika piksela na samomodyfikujące się operandy:
  około 2 zaoszczędzone cykle adresowania pochłaniają droższe zapisy
  operandów. Brak uzasadnionego budżetu >=0,05 FPS; nie wdrożono.
- Cache między klatkami: nie wykazano wystarczającej niezmienności danych
  i oszczędności >=0,05 FPS. Nie wprowadzano przybliżeń ani zmiany logiki.
- Punkty 5..8 wcześniejszego audytu pozostają odłożone na życzenie
  użytkownika; ich opis jest w OPCJE_OPTYMALIZACJI_V5_PL.md.
To nie dowód absolutnego optimum. Dalszy pomysł musi przejść ten sam
próg oszacowania i test dokładności, zanim otrzyma czas implementacji.

WERYFIKACJA
- Geometria: 1000 losowych przypadków czterech orientacji i 58 pełnych
  wywołań $8309; cały RAM poza martwym stosem i wszystkie rejestry/flag.
- Emulator: 40 wejść geometrii, jawnie wybrane wszystkie cztery tablice,
  porównanie z CPU wykonującym v6; zgodne tablice, rejestry i odtworzone $9F.
- Obcinanie: 3000 losowych przypadków oraz renderer+wypełnianie 58 scen;
  zgodność całego RAM poza martwym stosem i A/X/Y/P/SP.
- Integracja: 256 wejść czyszczenia, osłona banków 2,5,6,8..14 oraz
  232 pełne VBI, zgodność stanu przy stałych wejściach sprzętowych testu CPU.
- Zimny start, 2000 klatek lotu, próby poziomów 10/26 po 3000 klatek,
  START z banków 5,6,8,9,10,11,12,13,14 i ponowny zimny start: bez zawieszeń.
  W bankach 10..13 START następuje po zachowaniu $9F na stosie; wybór
  orientacji jest jawnie wymuszonym wejściem testowym. Na poziomie 10
  lot środkowy oraz wszystkie loty poziomu 26 kończą w trybie 0, więc
  nie opisujemy ich jako nieprzerwanego lotu przez cały okres.
- Ręczna kontrola końcowego obrazu lotu. Screeny pozostają lokalnie.

Poprawki narzędzi testowych: punkt końcowy $84FD należy sprawdzać wraz
z bankiem 2, także w modelu CPU; ten sam adres występuje w kodzie bankowym.
Wspólny adres pierwszej instrukcji po prologu to $800F, a nie $8010
(w części banków $8010 jest operandem). Te błędy dotyczyły testów;
nie zmieniały ROM-u ani zmierzonych wariantów benchmarku.

ODTWORZENIE I KOPIA
ROM SHA256: {sha(rom)}
python scripts/rebuild_v7.py --mads PEŁNA_ŚCIEŻKA_DO_MADS
Builder odtwarza v1..v7 bez SDK, dumpów i stanów emulatora; sprawdza ROM,
CAR i IPS. Stare stany sprzed v6 wymagają nadal podmiany kodu RAM $7EEB;
normalne uruchamianie odbywa się przez zimny start pliku CAR.
Repo zawiera wybrane źródła, raporty i zwarte wyniki, bez surowych profili,
screenów, dumpów, stanów i narzędzi. Odtworzenie identycznych dawnych lotów
po utracie stanów nie jest możliwe: należy zebrać nowe wejścia i pomiary.
'''
(OUT/'RAPORT_V7_PL.txt').write_text(report,encoding='utf-8')
(dist/'README-v7_PL.txt').write_text('Wydanie v7, PAL, XEGS 128 KiB (CART 14). Użyj zimnego startu pliku CAR.\nRaport w repo: ../docs/WYDANIE_V7_PL.txt\nRaport lokalny: ../results/research_v6/RAPORT_V7_PL.txt\nROM SHA256: '+sha(rom)+'\n',encoding='utf-8')
print(json.dumps({'fps':fps,'gain_v6':stats['gain_vs_v6_percent'],'gain_original':stats['gain_vs_original_percent'],'sha256':sha(rom)},indent=2))
