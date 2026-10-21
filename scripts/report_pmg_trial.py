from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/pmg_trial'
rows=[r for r in json.loads((ROOT/'results/opt14/benchmark.json').read_text()) if r['variant'] in ('buffer_sync','pmg_trial')]
fps={}
for v in ('buffer_sync','pmg_trial'):
 rr=[r for r in rows if r['variant']==v];assert len(rr)==4 and all(r['mode']==2 for r in rr)
 fps[v]=sum(r['intervals'] for r in rr)*(3546895/2)/sum(r['ticks'] for r in rr)
rom=(ROOT/'build/pmg_trial.rom').read_bytes();digest=hashlib.sha256(rom).hexdigest()
checks={}
for n in ('cpu-tests','bar-invariant','stress'):
 checks[n]=json.loads((OUT/f'{n}.json').read_text());assert checks[n]['result']=='pass' and checks[n]['rom_sha256']==digest
delta=fps['pmg_trial']-fps['buffer_sync'];accepted=delta>=0.05
summary={'rom_sha256':digest,'fps':fps,'delta_fps':delta,'percent':100*delta/fps['buffer_sync'],'meets_0_05_fps_threshold':accepted,'benchmark':rows,'baseline':'v8 standard four-scenario measurement','status':'candidate_requires_release_review' if accepted else 'not_promoted_v8_remains_recommended'}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2));(OUT/'benchmark.json').write_text(json.dumps(rows,indent=2))
table='\n'.join(f"| {s} | {next(r['fps'] for r in rows if r['variant']=='buffer_sync' and r['scenario']==s):.6f} | {next(r['fps'] for r in rows if r['variant']=='pmg_trial' and r['scenario']==s):.6f} |" for s in ('straight','right','left','fast_right'))
text=f'''# Pierwsza próba optymalizacji PMG na bazie v8

21.10.2026. Eksperyment, nie nowe wydanie. ROM SHA256: `{digest}`.

## Wynik

| Lot | v8 | Próba PMG |
|---|---:|---:|
{table}

Łączny wynik: v8 **{fps['buffer_sync']:.6f} FPS**, próba **{fps['pmg_trial']:.6f} FPS**.
Różnica **{delta:+.6f} FPS**, **{summary['percent']:+.3f}%**.
Próg +0,05 FPS: **{'osiągnięty w tym pomiarze' if accepted else 'nieosiągnięty'}**.
{'Wariant wymaga decyzji o wydaniu po ocenie zakresu testów.' if accepted else 'Nie promowano próby do nowego wydania. Zalecanym wydaniem pozostaje v8.'}

Metoda: suma prezentacji w $B516 podzielona przez sumę czasu PAL,
cztery standardowe scenariusze po co najmniej 3000 ramek, rozgrzewka 50.
Baza to zachowany pomiar v8 z tego samego protokołu i stanów wejściowych.
Nie jest to średnia arytmetyczna czterech FPS. Zmiana szybkości może
zmieniać przebieg lotu; pojedyncza seria nie daje przedziału ufności.

## Co zmieniono

- Pasek $A55C: aktualizacja różnicowa. Dla spójnego poprzedniego obrazu
  zapisuje |nowa-stara| bajtów zamiast 57. Przy starej wartości zero lub
  wartościach poza zakresem 0..55 używa oryginalnego pełnego odrysowania.
  Stara wartość zero obejmuje inicjalizację po zerowaniu stanu $2830..$28D5.
  Gdy obie wartości są równe, oryginalne pominięcie aktualizacji pozostaje.
- Kopia 21 wierszy: siedem iteracji po trzy wiersze; końcowy licznik $BD=0.
- Kasowanie i kopiowanie 5 wierszy: rozwinięte pętle, zachowane X/Y i $BB.
- Dwie pętle po 3 wiersze pocisku: rozwinięte, zachowane maski innych pocisków.

Kod zajmuje wolne miejsca banku 2: $83CA..$8470 oraz $84B0..$84F3.
Nie narusza clippingu $8380..$83C9, osłony buforów $84A0..$84AE ani
kontynuacji geometrii $84FD. Bez dodatkowego banku i bez nowej zmiennej RAM.
Kod jest wywoływany z VBI, którego istniejąca osłona udostępnia bank 2.
Nie stosowano SMC; te proste warianty go nie wymagają.

## Weryfikacja

- {checks['cpu-tests']['cases']} przypadków CPU: wszystkie 56x56 przejść paska
  ze spójnym poprzednim obrazem, 300 przypadków ścieżki pełnego odrysowania,
  po 600 przypadków trzech pozostałych procedur i 32 zachowane wejścia z gry.
  Zgodność całego RAM poza martwym stosem, GTIA oraz A/X/Y/P/SP.
- 320 wejść do obsługi paska w emulatorze: po 80 po zimnym starcie,
  w podstawowym locie oraz w stanach poziomów 10 i 26. Za każdym razem
  poprzedni niezerowy stan odpowiadał rzeczywistym bajtom paska.
- Zimny start, lot, próby poziomów 10/26, restart z banków rozszerzeń
  i ponowny start: testy przeszły. Niektóre próby kończą się trybem 0,
  więc nie oznaczają nieprzerwanego lotu przez cały test.

W modelu CPU zmieniona kopia 21 wierszy oszczędza 106 cykli na aktywne
wywołanie, obsługa 5 wierszy do 44, a 3 wierszy do 12. Pomijane aktualizacje
nie zyskują. Pasek może być wolniejszy przy dużym skoku: najgorsza różnica
w wyczerpującym teście przejść to 233 cykle więcej. Nie dobierano dalszego
progu przełączania na pełne odrysowanie w ramach tej pierwszej próby.

## Ograniczenia i odtworzenie

Aktualizacja różnicowa zakłada spójność starej wartości i pamięci obrazu.
Testy obejmują wymienione scenariusze, nie każdą możliwą sekwencję rozgrywki.
Stare zewnętrzne save-state'y z niespójnym stanem nie są objęte gwarancją.
Nie testowano fizycznego Atari ani wszystkich wariantów animacji PMG.

Źródła: src/pmg_short_loops.asm, src/pmg_bar_delta.asm.
Budowanie lokalne: python scripts/build_pmg_trial.py, wymaga build/buffer_sync.rom
i MADS w tools/mads/bin/windows_x86_64/mads.exe. Skrypt generuje te źródła.
Testy: scripts/test_pmg_trial.py, scripts/validate_pmg_trial.py,
scripts/stress_pmg_trial.py. Część testów wymaga zachowanych lokalnych stanów.
Binaria eksperymentu: build/pmg_trial.rom i build/pmg_trial.car.
Nie zastąpiono plików v8 w dist.
'''
(OUT/'PROBA_PMG_PL.md').write_text(text,encoding='utf-8');print(json.dumps(summary,indent=2))
