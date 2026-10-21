import pathlib,json,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'results/pmg_trial';dist=ROOT/'dist';sha=lambda d:hashlib.sha256(d).hexdigest()
rom=(ROOT/'build/pmg_trial.rom').read_bytes();digest=sha(rom)
for n in ('cpu-tests','bar-invariant','initialization','stress'):
 d=json.loads((OUT/f'{n}.json').read_text());assert d['result']=='pass' and d['rom_sha256']==digest
performance=json.loads((OUT/'summary.json').read_text());assert performance['rom_sha256']==digest
performance['status']='released_v9';performance['threshold_exception']='User explicitly accepted the small gain after the first trial; this does not change the default threshold for future work.'
stem='Rescue on Fractalus! - PAL optimized v9 128KB'
(dist/f'{stem}.rom').write_bytes(rom);(dist/f'{stem}.car').write_bytes((ROOT/'build/pmg_trial.car').read_bytes())
original=(ROOT/'Rescue on Fractalus!.rom').read_bytes();ips=bytearray(b'PATCH');pos=0
while pos<len(rom):
 if pos<len(original) and rom[pos]==original[pos]:pos+=1;continue
 start=pos
 while pos<len(rom) and (pos>=len(original) or rom[pos]!=original[pos]) and pos-start<65535:pos+=1
 ips+=start.to_bytes(3,'big')+(pos-start).to_bytes(2,'big')+rom[start:pos]
ips+=b'EOF';(dist/'fractalus-pal-optimized-v9-128KB.ips').write_bytes(ips)
(OUT/'release-v9.json').write_text(json.dumps(performance,indent=2))
(dist/'build-manifest-v9.json').write_text(json.dumps({'sha256':digest,'rom_bytes':len(rom),'cart_type':14,'original_sha256':sha(original),'performance':performance,'sources':{n:sha((ROOT/n).read_bytes()) for n in ('src/pmg_short_loops.asm','src/pmg_bar_delta.asm','scripts/build_pmg_trial.py','scripts/rebuild_v9.py')}},indent=2))
report=f'''# Wydanie v9 — niewielka optymalizacja PMG

21.10.2026. Atari XL/XE PAL, 64 KiB RAM, XEGS 128 KiB / CART 14.

Wydano dokładnie przetestowany wariant PMG, bez dalszych zmian binarnych.
Użytkownik zaakceptował ten konkretny zysk poniżej dotychczasowego progu
+0,05 FPS, pod warunkiem małej złożoności i bezpieczeństwa. Nie zmieniono
automatycznie progu dla przyszłych eksperymentów.

## Wynik

v8: **7,720697 FPS**. v9: **7,764418 FPS**.
Różnica: **+0,043721 FPS (+0,566%)** w standardowym zestawie czterech lotów.
Nie wykonano ponownego pomiaru identycznego ROM-u przy samym nadaniu numeru
wydania. Wyniki i ograniczenia pierwszej serii są w PROBA_PMG_PL.md.
Trzy scenariusze zyskały, szybki lot w prawo nieco zwolnił. Nie jest to
gwarancja przyspieszenia każdego lotu ani wynik serii statystycznej.

## Zakres i bezpieczeństwo

- Pasek PMG $A55C: zapisuje tylko zmieniony odcinek. Dla starej wartości
  zero oraz danych poza zakresem 0..55 zachowuje pełne odrysowanie.
- Pętle 3/5 wierszy rozwinięto, a 21 wierszy kopiuje się po trzy na iterację.
- Bez zmiany formatu cartridge'a, jakości obrazu i matematyki terenu.
- Zachowano naprawę synchronizacji buforów z v8.
- Kod pomocniczy: bank 2, $83CA..$8470 i $84B0..$84F3. Nie nakłada się
  na clipping $8380..$83C9, osłonę $84A0..$84AE ani kontynuację $84FD.
  Wejścia są w VBI z już aktywnym bankiem 2; bank powrotny zachowuje
  istniejąca osłona przerwania. Brak nowych zmiennych i samomodyfikacji.

Weryfikacja obejmuje 5268 przypadków porównawczych CPU, 320 kontroli
spójności paska oraz zimny start, poziomy 10/26 i restarty z banków
rozszerzeń. Przed wydaniem dodatkowo porównano pierwszych 40 rzeczywistych
wywołań obsługi paska po zimnym starcie z oryginalną procedurą v8:
pierwsza zmiana 0→29 wykonała poprawne pełne odrysowanie, kolejne
aktualizacje zachowały zgodność całego RAM poza martwym stosem oraz
rejestrów i flag. Wynik: initialization.json.

To ograniczona, sprawdzona zmiana, ale nie dowód poprawności każdej
możliwej sekwencji rozgrywki. Testy odbyły się w modelu CPU i Altirrze
headless, nie na fizycznym Atari. Zalecany zimny start CAR v9; nie należy
przenosić starego save-state'u z arbitralnie niespójnym stanem PMG.

## Pliki i odtworzenie

Gotowy plik: dist/{stem}.car
ROM SHA256: `{digest}`
Odtworzenie offline: `python scripts/rebuild_v9.py --mads ŚCIEŻKA_DO_MADS`.
Builder sprawdza zgodność ROM-u, CAR-a i łatki IPS do oryginalnego ROM-u.
Wcześniejsze wydania pozostają w dist. Historyczny raport pierwszej próby
nadal opisuje decyzję sprzed późniejszej zgody użytkownika na wydanie.

Nie wdrażano pozostałych pomysłów audytu PMG. Ich opis zachowano
w AUDYT_PMG_PL.md; nie należy traktować ich jako już przetestowanych poprawek.
'''
(OUT/'WYDANIE_V9_PL.md').write_text(report,encoding='utf-8')
(dist/'README-v9_PL.txt').write_text('v9: mała optymalizacja PMG na bazie v8. PAL, XEGS 128 KiB / CART 14.\nUruchom CAR przez zimny start. Pomiar 7,764418 FPS, +0,043721 względem v8.\nRaport w repo: docs/WYDANIE_V9_PL.md.\nROM SHA256: '+digest+'\n',encoding='utf-8')
print('v9 packaged',digest)
