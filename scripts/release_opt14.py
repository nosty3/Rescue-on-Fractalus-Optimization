"""Package validated four-stage optimization and Polish findings."""
import pathlib,json,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'results/opt14';dist=ROOT/'dist'
rom=(ROOT/'build/opt14_interpolation.rom').read_bytes();sha=lambda d:hashlib.sha256(d).hexdigest()
for name in ('division-tests','division-vbi-tests','width45-random','opt14_width45-renderer-tests','geometry-tests','interpolation-tests','integration-tests','stress'):
 data=json.loads((OUT/f'{name}.json').read_text());assert data['result']=='pass',name
stress=json.loads((OUT/'stress.json').read_text());assert stress['rom_sha256']==sha(rom)
bench=json.loads((OUT/'benchmark.json').read_text());variants=['opt14_base','opt14_division','opt14_width45','opt14_geometry','opt14_interpolation'];fps={}
for name in variants:
 rows=[r for r in bench if r['variant']==name];assert len(rows)==4 and all(r['mode']==2 for r in rows)
 fps[name]=sum(r['intervals'] for r in rows)*(3546895/2)/sum(r['ticks'] for r in rows)
stem='Rescue on Fractalus! - PAL optimized v6 128KB'
(dist/f'{stem}.rom').write_bytes(rom);(dist/f'{stem}.car').write_bytes((ROOT/'build/opt14_interpolation.car').read_bytes())
original=(ROOT/'Rescue on Fractalus!.rom').read_bytes();assert sha(original)=='1eb18e2a1ff31f43871a5e4e21e73f61b7659177d33d2cdbb29f36530b9f4d68'
ips=bytearray(b'PATCH');pos=0
while pos<len(rom):
 if pos<len(original) and rom[pos]==original[pos]:pos+=1;continue
 start=pos
 while pos<len(rom) and (pos>=len(original) or rom[pos]!=original[pos]) and pos-start<65535:pos+=1
 ips+=start.to_bytes(3,'big')+(pos-start).to_bytes(2,'big')+rom[start:pos]
ips+=b'EOF';(dist/'fractalus-pal-optimized-v6-128KB.ips').write_bytes(ips)
summary={'result':'pass','fps_method':'sum presentations / sum emulated time, 4 scenarios, >=3000 PAL frames each','fps':fps,'gain_vs_v5_percent':100*(fps[variants[-1]]/fps[variants[0]]-1),'gain_vs_original_percent':100*(fps[variants[-1]]/6.553531221-1),'scenarios':bench,'rom_sha256':sha(rom)}
(OUT/'final-summary.json').write_text(json.dumps(summary,indent=2))
manifest={'sha256':sha(rom),'rom_bytes':len(rom),'cart_type':14,'original_sha256':sha(original),'performance':summary,'sources':{p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for pattern in ('src/opt14_*.asm','scripts/build_opt14_*.py','scripts/rebuild_v6.py') for p in ROOT.glob(pattern)}}
(dist/'build-manifest-v6.json').write_text(json.dumps(manifest,indent=2))
table='\n'.join(f'{name:24} {fps[name]:.6f}' for name in variants)
scenes='\n'.join(f"{scenario:16} "+' '.join(f"{next(r['fps'] for r in bench if r['scenario']==scenario and r['variant']==v):.6f}" for v in variants) for scenario in ('straight','right','left','fast_right'))
report=f'''CZTERY OPTYMALIZACJE — WYDANIE v6, 21.10.2026
Atari XL/XE PAL, 64 KiB RAM, cartridge XEGS 128 KiB (CART 14).

WYNIK
{table}
Zysk v6 względem v5: {summary['gain_vs_v5_percent']:.3f}%.
Zysk względem oryginału 6,553531 FPS: {summary['gain_vs_original_percent']:.3f}%.
Średnia to suma prezentacji podzielona przez sumę czasu emulowanego.
Mierzymy nowe obrazy lotu przy $B516, nie częstotliwość odświeżania PAL.
Każdy wariant: cztery loty po co najmniej 3000 klatek PAL, ten sam stan
początkowy, rozgrzewka 50 klatek, te same kierunki i opcja szybkiego lotu.
Szybsza gra może przelecieć inną drogę w tym samym czasie: wyniki etapów
nie są czystym pomiarem kosztu jednej instrukcji ani gwarancją FPS wszędzie.

Scenariusz       v5       pkt1     +pkt2    +pkt3    +pkt4=v6
{scenes}

1. DZIELENIE $8224
Pominięto normalizację licznika i mianownika, zachowując właściwy algorytm
dzielenia. Zmiana pięciu bajtów prowadzi do $8235 zamiast $8231.
Warunki: 0 <= N < D < 32768, tryb binarny. Pomocnicze $AE..$B1 pozostają
nieznormalizowane; nie obiecujemy zgodności tych martwych bajtów.
20033 przypadki, 58 scen i następujące procedury: zgodne wyniki.
232 przebiegi VBI nie czytają tych bajtów. Łącznie renderer oszczędza
176642 cykle CPU w zestawie 58 scen. Nie zajmuje nowych banków.

2. PROFIL GÓR: SZEROKOŚCI 4 I 5
Dodano wyspecjalizowane rozgałęzienia dla głębokości 1..4 w banku 5.
Zachowano zaokrąglenia, clipping i oba potomne fragmenty; to nie jest LOD.
Zmierzono osiem zestawów głębokości. Wybrany oszczędza 14422 cykle
w 58 pełnych scenach. 6000 przypadków losowych i brzegowych: zgodność.
Średni przyrost FPS jest mały, niższy od wcześniejszego szacunku; dwa
scenariusze są wolniejsze od samego punktu 1. Zachowano ten wariant,
bo zmniejsza zmierzony koszt CPU i nieznacznie poprawia zbiorczy wynik.
Bez kolejnych przełączeń banku; wykorzystuje wolny koniec banku 5.

3. STAŁE KOMENDY GEOMETRII
Cztery tablice po 45 komend ($9A55/$9A82/$9AAF/$9ADC) przekształcono
w cztery programy w bankach 10..13. Wyeliminowano odczyty i dekodowanie
komend oraz część indeksowania. Wspólny ogon punktu zachowuje obliczenia.
1000 losowych przypadków, 58 pełnych wywołań $8309: zgodność całego RAM
poza martwym stosem oraz A/X/Y/P/SP. Oszczędność: 82736 cykli / 58 scen.
30 rzeczywistych wywołań w emulatorze porównano z oryginalnym kodem CPU.
Wejście bank2 $835E -> $9863; przełączenie $9890; kontynuacja $9893.
Powrót bank10..13 $98E0 -> bank2 $98E7 -> $84FD.
Osłona VBI przy $BFEA akceptuje teraz znaczniki banków mniejsze od 15.

4. DOKŁADNA INTERPOLACJA TABLICOWA I SMC
Bank 14 zawiera 16 stron wkładów arytmetycznych oraz tablicę value>>4.
Zastępują wielokrotne przesunięcia i dodawania bez zmiany zaokrągleń.
Istniejący RAM $7EEB..$7FC1 zawiera trampolinę i prywatny helper $7F20.
Osiem operandów jest samomodyfikujących; wszystkie ustawiane przed użyciem.
Nie zużywa dodatkowego obszaru RAM. Ładowarka kopiuje nowy kod z banku 1.
DLI nie używa helpera. Procedura przywraca bank2; osłona VBI przywraca
bank przerwanej części renderera. Samo SEI nie chroniłoby przed NMI.
5000 przypadków z losowymi danymi i zatrutymi operandami SMC: zgodność
RAM poza zastąpionym kodem i martwym stosem, wszystkie rejestry i flagi.
Oszczędność 314..339, średnio 326,4432 cyklu na wywołanie, z bankowaniem.

TESTY INTEGRACYJNE I OGRANICZENIA
- Wszystkie 256 wartości X czyszczenia $9214: zgodność z bazą.
- Powrót VBI do banków 2,5,6,8,9,10,11,12,13,14: poprawny.
- 58 scen x 4 pełne VBI: zgodny RAM (poza kodem/stosem), rejestry i flagi.
- Zimny start, 2000 klatek lotu, sześć prób START z banków 5,6,8,9,12,14,
  ponowny zimny start i lot: poprawne, sygnatura kodu RAM zachowana.
- Poziomy 10 i 26, trzy kierunki x 3000 klatek. Na poziomie 26 wszystkie
  próby kończą w trybie 0; nie zaliczamy ich jako ciągłego lotu bez końca gry.
- Test CPU ma stałe wejścia sprzętowe; rzeczywiste PAL/DMA/przerwania
  sprawdza osobno emulator. Testy nie są dowodem dla wszystkich stanów gry.
- Ręcznie sprawdzono obraz końcowy lotu; screenshoty zostają lokalnie.

ODRZUCONE WYNIKI I PUŁAPKI
Pierwsza trampolina geometrii kolidowała z zapasową ścieżką czyszczenia.
Przeniesiono ją do nieużywanego ciała starego renderera w banku 2.
Brak JMP w selektorze banku 12 powodował wykonanie wypełnienia FF.
py65 ignorował nieobsługiwany opcode, a rzeczywisty NMOS modyfikował RAM.
Naprawiono skok i dodano ścisłe odrzucanie nieobsługiwanych instrukcji.
Wcześniejsze wyniki ok. 8..10,7 FPS są BŁĘDNE i wykluczone z raportu.
Nie używać starych save-state bez podmiany RAM $7EEB..$7FC1; benchmark
stosuje patch_state(), a zwykły zimny start sam ładuje właściwy kod.

BANKI I ODTWORZENIE
Rozmiar nadal 128 KiB. Banki 10..13: geometria; bank14: interpolacja.
Nie ma już całkowicie pustych banków z puli 10..14; zostają luki wewnątrz.
Bank7 nie został uznany za wolny. Nie potrzeba dodatkowego RAM Atari.
ROM SHA256: {sha(rom)}
Odtworzenie offline z kopii repozytorium:
python scripts/rebuild_v6.py --mads PEŁNA_ŚCIEŻKA_DO_MADS
Builder odtwarza v1..v6 i weryfikuje ROM/CAR/IPS bez SDK i stanów emulatora.
Generatory i testy historyczne wymagają lokalnych fixture/state; zgodnie
z zakresem kopii nie publikujemy dumpów RAM, screenów i stanów. Po utracie
tych plików można odtworzyć grę, lecz trzeba zebrać nowy materiał testowy.

PUNKTY 5..8 — ODŁOŻONE NA ŻYCZENIE UŻYTKOWNIKA
5. Wyrównanie stron w gorących pętlach i tablicach.
6. Wspólna tablica mnożenia dla $7CD6.
7. Ograniczenie kosztu skanowania kanałów dźwięku bez zmiany zachowania.
8. Specjalizacja późnych początkowych wierszy wypełniania 33..48.
Nie wdrożono ich. Historyczne oszacowania i uzasadnienia zachowano
w docs/OPCJE_OPTYMALIZACJI_V5_PL.md; są hipotezami, nie wynikami v6.
'''
(OUT/'RAPORT_V6_PL.txt').write_text(report,encoding='utf-8')
(dist/'README-v6_PL.txt').write_text('Wydanie v6: użyj pliku CAR (XEGS 128 KiB, typ 14).\nRaport: ../docs/WYDANIE_V6_PL.txt w kopii repozytorium.\nLokalny raport: ../results/opt14/RAPORT_V6_PL.txt.\nNie wczytuj starych stanów emulatora: zawierają dawny kod RAM.\nSHA256 ROM: '+sha(rom)+'\n',encoding='utf-8')
print(json.dumps({'fps':fps,'gain':summary['gain_vs_v5_percent'],'sha256':sha(rom)},indent=2))
