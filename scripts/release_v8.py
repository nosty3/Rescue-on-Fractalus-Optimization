"""Package the tested buffer ownership fix and compact evidence."""
import pathlib, json, hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]; OUT=ROOT/'results/buffer_race'; dist=ROOT/'dist'
sha=lambda d:hashlib.sha256(d).hexdigest()
rom=(ROOT/'build/buffer_sync.rom').read_bytes(); digest=sha(rom)
for name in ('cpu-tests','sync-validation','stress'):
    data=json.loads((OUT/f'{name}.json').read_text()); assert data['result']=='pass'
    if 'rom_sha256' in data: assert data['rom_sha256']==digest
all_rows=json.loads((ROOT/'results/opt14/benchmark.json').read_text())
bench=[r for r in all_rows if r['variant'] in ('v7_clipping','buffer_sync')]
fps={}
for v in ('v7_clipping','buffer_sync'):
    rows=[r for r in bench if r['variant']==v]; assert len(rows)==4 and all(r['mode']==2 for r in rows)
    fps[v]=sum(r['intervals'] for r in rows)*(3546895/2)/sum(r['ticks'] for r in rows)
stem='Rescue on Fractalus! - PAL optimized v8 128KB'
(dist/f'{stem}.rom').write_bytes(rom); (dist/f'{stem}.car').write_bytes((ROOT/'build/buffer_sync.car').read_bytes())
original=(ROOT/'Rescue on Fractalus!.rom').read_bytes(); ips=bytearray(b'PATCH'); pos=0
while pos<len(rom):
    if pos<len(original) and rom[pos]==original[pos]: pos+=1; continue
    start=pos
    while pos<len(rom) and (pos>=len(original) or rom[pos]!=original[pos]) and pos-start<65535: pos+=1
    ips+=start.to_bytes(3,'big')+(pos-start).to_bytes(2,'big')+rom[start:pos]
ips+=b'EOF'; (dist/'fractalus-pal-optimized-v8-128KB.ips').write_bytes(ips)
race={}
for v in ('original','v7_clipping'):
    rows=json.loads((OUT/f'{v}-race.json').read_text())
    race[v]={'clear_entries':len(rows),'pending_presentation':sum(r['ready']!=0 for r in rows)}
summary={'result':'pass','rom_sha256':digest,'fps':fps,'delta_fps':fps['buffer_sync']-fps['v7_clipping'],'gain_vs_original_percent':100*(fps['buffer_sync']/6.553531221-1),'race_before':race,'safe_clear_checks':240,'visual_observation':{'continuous_frames_per_variant':3000,'v7_glitch_example_frame':237,'fixed_sample_review':'no matching wedge seen in reviewed candidates; candidate detector also flags normal terrain changes, not a proof of zero artifacts'},'scenarios':bench}
(OUT/'final-summary.json').write_text(json.dumps(summary,indent=2)); (OUT/'benchmark.json').write_text(json.dumps(bench,indent=2))
(dist/'build-manifest-v8.json').write_text(json.dumps({'sha256':digest,'rom_bytes':len(rom),'cart_type':14,'original_sha256':sha(original),'performance':summary,'sources':{name:sha((ROOT/name).read_bytes()) for name in ('src/buffer_sync.asm','scripts/build_buffer_sync.py','scripts/rebuild_v8.py')}},indent=2))
table='\n'.join(f"{s:12} {next(r['fps'] for r in bench if r['variant']=='v7_clipping' and r['scenario']==s):.6f}  {next(r['fps'] for r in bench if r['variant']=='buffer_sync' and r['scenario']==s):.6f}" for s in ('straight','right','left','fast_right'))
report=f'''WYDANIE v8 — NAPRAWA JEDNOKLATKOWEGO KLINA PO LEWEJ STRONIE
21.10.2026. PAL, XEGS 128 KiB, typ CART 14.

OBJAW I ODTWORZENIE
Użytkownik zauważył brązowy fragment po lewej stronie w Atari800Win
Plus4beta i Altirra 4.40, również we wcześniejszych wydaniach.
W lokalnej Altirrze headless odtworzono odpowiadający mu klin w v7:
lot w prawo, 50 klatek rozgrzewki, klatka 237 ciągłego zapisu obrazu.
Screeny i stany pozostają lokalnie w results/buffer_race, poza repo.
Nie wykonywano testów w GUI wskazanych przez użytkownika emulatorów.

PRZYCZYNA
Główna pętla publikuje nowy obraz przez STA $42 ($A34A/$A3AF).
VBI przełącza listę ANTIC, a następnie potwierdza to przez STA $42
w $B518 (zero przygotowane w $B516). Główna pętla mogła jednak wejść
do czyszczenia $9214 przed tym potwierdzeniem. Czyściła wówczas bufor
wciąż wyświetlany. Kolejność czyszczenia kolumn od lewej wyjaśnia
jednostronny kształt artefaktu. Szybszy renderer zmienia fazę względem
wiązki i może zwiększać widoczność tego błędu synchronizacji.
W zachowanych próbach wejść do czyszczenia: {race}.
Nie każde wejście z niezerowym $42 daje widoczny klin: zależy od wiązki.
Warunek wyścigu wykryto również w oryginalnym ROM-ie; nie jest to
pomiar częstości widocznych artefaktów w oryginale ani w każdym buildzie.
Poprzednie testy matematyki i końcowych buforów nie sprawdzały momentu
zapisu względem ANTIC. To luka wcześniejszej walidacji.

POPRAWKA
Bank 2: $9214 JMP $84A0 zamiast JMP $982F. Nowy kod $84A0..$84AE
czeka na wyzerowanie $42 przez VBI przed rozpoczęciem czyszczenia.
Obliczenia geometrii mogą nadal wyprzedzać prezentację. A/X/Y/P/SP
są zachowane. Dwa dodatkowe bajty stosu tylko na czas osłony.
W trybie $4A=0 oczekiwanie jest pomijane (VBI nie potwierdza wtedy obrazu).
Kod mieści się w nieużywanym fragmencie dawnego interpretera, poza
nowym clippingiem $8380..$83C9 i przed kontynuacją $84FD.
Nie zmienia matematyki, jakości terenu ani rozmiaru cartridge'a.

WYNIK WYDAJNOŚCI
Scenariusz    v7         v8
{table}
Łącznie v7: {fps['v7_clipping']:.6f} FPS; v8: {fps['buffer_sync']:.6f} FPS.
Różnica: {summary['delta_fps']:+.6f} FPS.
Względem historycznego oryginału 6,553531 FPS: +{summary['gain_vs_original_percent']:.3f}%.
To suma prezentacji przy $B516 / suma emulowanego czasu PAL w czterech
lotach po >=3000 klatek, a nie średnia arytmetyczna FPS ani odświeżanie PAL.
Wynik v7 pochodzi z poprzedniego pomiaru tym samym protokołem.
Zmienione tempo wpływa na przebieg lotu; brak serii statystycznych
powtórzeń i pomiaru na fizycznym Atari. Koszt oczekiwania jest konieczny
dla poprawnego używania dwóch buforów. Historycznych wyników v1..v7
nie należy przedstawiać jako wyników wersji wolnych od tego wyścigu.

WERYFIKACJA
- CPU: 256 wartości X przy wejściu do czyszczenia; zgodność RAM poza
  martwym stosem i pełnego stanu rejestrów/flag względem v7.
- Cztery przypadki oczekiwania na prezentację: brak zapisu do obrazu
  przed potwierdzeniem, poprawny powrót po nim; obejście poza lotem.
- Emulator: 240 kolejnych wejść do właściwego czyszczenia z $42=0.
- START podczas oczekiwania, zimny start, lot, poziomy 10/26,
  START z banków 5,6,8,9,10,11,12,13,14 i ponowny start: testy przeszły.
  Próby poziomów mogą kończyć się trybem 0; nie są deklaracją nieprzerwanego lotu.
- Ciągła obserwacja 3000 klatek PAL obu wersji. W v7 zarejestrowano klin;
  w przejrzanych kandydatach v8 tego klina nie zaobserwowano. Prosty
  detektor zmian po lewej zgłasza też prawidłowe zmiany terenu: jego
  wyniku nie traktujemy jako automatycznego dowodu braku wszelkich gliczy.
- Odtworzenie offline ROM/CAR/IPS z MADS jest sprawdzane osobno.

DALSZE PRACE
Przed kolejnym przyspieszaniem utrzymać test własności bufora. Oczekiwania
nie wolno usuwać dla poprawy FPS. Można badać przesuwanie pracy niezapisującej
obrazu przed oczekiwanie, ale dopiero po dowodzie rozłączności danych
i oszacowaniu zysku >=0,05 FPS. Trzeci bufor wymaga analizy dostępnego RAM
oraz list ANTIC; dodatkowe banki ROM same nie rozwiązują wyścigu.
Drobne punkty 5–8 wcześniejszego audytu pozostają odłożone.

URUCHOMIENIE I ODTWORZENIE
Użyć zimnego startu pliku CAR v8, zamiast dawnego zapisu stanu.
python scripts/rebuild_v8.py --mads ŚCIEŻKA_DO_MADS
ROM SHA256: {digest}
Do odtworzenia binariów nie potrzeba SDK, dumpów ani stanów emulatora.
Testy dawnych lotów wymagają lokalnych stanów; po utracie komputera trzeba
zebrać nowe wejścia. Repo przechowuje kod testów i zwarte podsumowania.
'''
(OUT/'RAPORT_V8_PL.txt').write_text(report,encoding='utf-8')
(dist/'README-v8_PL.txt').write_text('v8: naprawa synchronizacji buforów i klina po lewej. PAL, XEGS 128 KiB / CART 14.\nUruchom CAR przez zimny start. Raport: docs/WYDANIE_V8_PL.txt w repo.\nROM SHA256: '+digest+'\n',encoding='utf-8')
print(json.dumps(summary,indent=2))
