"""Polish report for the PAL repetition of the native-boot FPS experiment."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/pal_isolated_main'
d=json.loads((OUT/'benchmark.json').read_text())
s=json.loads((OUT/'summary.json').read_text())
ntsc=json.loads((ROOT/'results/ntsc_isolated_main/summary.json').read_text())
n=d['metadata']['count_per_version'];g=s['windows']['60'];ng=ntsc['windows']['60']
def f(x,k=4):return f'{x:.{k}f}'.replace('.',',')
lines=['# PAL — powtórzenie automatycznego testu oryginału i v9','',
f"Wykonano {n} natywnych startów każdej wersji. Średni FPS: oryginał **{f(g['original']['mean'])}**, v9 **{f(g['v9']['mean'])}**, zysk **{f(g['gain_percent'],2)}%**.",'',
'## Protokół ustalony przed pomiarem','',
'- Atari 800XL, 64 KB, PAL, standardowe dodatki, bez przyspieszaczy. Te same obrazy oryginału i v9 oraz ten sam emulator co w badaniu NTSC.',
'- Nowy proces emulatora dla każdego startu. Bez wczytywania stanów i modyfikowania pamięci gry.',
'- Dokładnie ten sam harmonogram 155 prób na wersję co w NTSC: START po 3000–3599 ramkach wideo, losowanie bez zwracania osobno dla każdej wersji. Bloki po pięć lotów każdej wersji.',
'- Pierwsze wejście $A32E, zwolnienie START, 170 ramek rozgrzewki, joystick wycentrowany. Bez skrętów, nurkowania, strzelania i dopalacza.',
'- Licznik odstępów między obrazami na $B516, zegar PAL 1 773 447,5 Hz. Ramka PAL ma 35 568 taktów (312 × 114).',
'- Punkty 15/30/60 sekund są kolejnymi oknami tego samego lotu, a nie niezależnymi próbami. Domykany jest pierwszy pełny odstęp po limicie.',
'- Przy wcześniejszym wyjściu z trybu lotu próba pozostaje w zbiorze. Liczone są pełne odstępy do ostatniego ukończonego obrazu lotu; animacja końca nie wchodzi do czasu. Reguła obowiązywała przed rozpoczęciem PAL.',
'- Cztery odizolowane emulatory, osobne porty/tokeny/pliki. Agregat zapisuje jeden wątek w kolejności planu. Każdy blok kończy się przed rozpoczęciem następnego.',
'- Liczbę 155 przyjęto przed pomiarem, aby powtórzyć NTSC. Nie wykonywano nowego pilota do doboru liczebności PAL i nie dobierano dalszych prób po obejrzeniu wyniku.','',
'170 ramek rozgrzewki trwa w PAL około 3,41 s, a w NTSC około 2,84 s. Również oczekiwanie w menu jest dłuższe w PAL. Zachowano liczbę ramek z protokołu, nie ich czas w sekundach. Właściwy limit pomiaru to 60 sekund czasu emulowanego Atari w obu standardach.','',
'## Walidacja techniczna','',
'Przed główną serią wykonano cztery 15-sekundowe scenariusze (dwa na wersję) sekwencyjnie i ponownie równolegle. Wszystkie odstępy między obrazami i pełne 32 KB RAM przy wejściu, po rozgrzewce i na końcu były identyczne. Te osiem lotów kontrolnych nie wchodzi do głównej średniej. Dane: ../pal_parallel_validation/validation.json.',
'Po zakończeniu sprawdzono zgodność 310 prób z planem, unikalność momentów START w każdej wersji, tryb PAL, hashe zdarzeń i RAM oraz ponownie przeliczono FPS z taktów. Wynik: integrity.json.','',
'## Wyniki','',
'| Limit | Oryginał FPS | SD | v9 FPS | SD | Zysk |','|---|---:|---:|---:|---:|---:|']
for sec,q in s['windows'].items():lines.append(f"| {sec} s | {f(q['original']['mean'])} | {f(q['original']['sd'])} | {f(q['v9']['mean'])} | {f(q['v9']['sd'])} | {f(q['gain_percent'],2)}% |")
lines+=['','## Niepewność i krótsze loty','']
for v in ('original','v9'):
    q=g[v];ci=q['mean_ci95'];t=q['measured_seconds_range']
    lines.append(f"- {v}: przybliżony przedział ufności 95% średniej {f(ci[0])}–{f(ci[1])} FPS; mediana {f(q['median'])}; {q['unique_maps']}/{n} różnych tablic terenu.")
    lines.append(f"- {v}: {q['shortened_flights']}/{n} lotów krótszych niż limit 60 s; zakres zmierzonych czasów {f(t[0],3)}–{f(t[1],3)} s.")
ci=g['gain_delta_normal_ci95'];cb=g['gain_stratified_bootstrap_ci95'];half=(ci[1]-ci[0])/2
lines += [f"- Zysk {f(g['gain_percent'],2)}%; przybliżony przedział ufności 95% {f(ci[0],2)}–{f(ci[1],2)}%, połowa szerokości {f(half,2)} p.p.",
f"- Bootstrap warstwowy (50 000 replikacji całych lotów wewnątrz blok/wariant): {f(cb[0],2)}–{f(cb[1],2)}%.",
f"- Kontrola ważenia czasem: {f(g['original']['pooled_fps'])} i {f(g['v9']['pooled_fps'])} FPS; zysk {f(g['pooled_gain_percent'],2)}%. Główny wynik nadaje każdemu lotowi jednakową wagę.",'',
'Przedziały są przybliżone. Analityczny przedział nie stosuje korekty na losowanie bez zwracania z 600 możliwych momentów START, co jest zachowawcze. Bootstrap utrzymuje zaobserwowane bloki; nie modeluje nieznanych zmian między przyszłymi sesjami. Dokładność dotyczy określonej populacji scenariuszy, nie całej gry.','',
'## Porównanie z NTSC','',
'| Standard | Oryginał FPS | v9 FPS | Zysk |','|---|---:|---:|---:|']
for label,q in [('PAL',g),('NTSC',ng)]:lines.append(f"| {label} | {f(q['original']['mean'])} | {f(q['v9']['mean'])} | {f(q['gain_percent'],2)}% |")
lines += ['',f"Różnica punktowych oszacowań zysku PAL minus NTSC: {f(g['gain_percent']-ng['gain_percent'],2)} p.p. To porównanie opisowe; nie jest osobnym testem równoważności standardów.",'',
'Te same momenty START wyrażone w ramkach nie gwarantują tych samych map ani trajektorii w różnych wersjach lub standardach. Wynik opisuje natywne uruchomienia przy wycentrowanym joysticku; nie jest pomiarem samego renderera na identycznych danych. Nie obejmuje kontrolowanego lotu w dolinach, skrętów ani innych poziomów.','',
'## Rozrzut i diagnostyka kolejności','']
for v,q in s['stability'].items():
    lines.append(f"- {v}: SD okna 60 s / SD okna 15 s = {f(q['sd_ratio_60_to_15'],3)}; korelacja z pozycją w harmonogramie rho={f(q['order_spearman']['rho'],3)}, p={f(q['order_spearman']['p'],3)}; Kruskal między blokami p={f(q['kruskal_blocks_p'],3)}.")
lines += ['', 'Diagnostyczne p nie są skorygowane na wielokrotne porównania ani dowodem równoważności małych bloków. Kolejność dotyczy zamrożonego harmonogramu, nie ścisłej kolejności ukończenia procesów.', '',
'## Materiały','',
'- plan.json, benchmark.json, summary.json, integrity.json — harmonogram, wyniki, statystyki i kontrola integralności.',
'- FPS_DISTRIBUTION_PAL_EN.png / .svg — rozkład FPS i dystrybuanta po angielsku.',
'- FLIGHT_DURATION_PAL_EN.png / .svg — zależność średniej od długości pomiaru po angielsku.',
'- scripts/benchmark_pal_parallel.py i pal_repro_common.py — wykonanie badania.',
'- scripts/summarize_ntsc_isolated.py main --video pal — statystyki.',
'- scripts/verify_ntsc_main_data.py --video pal — kontrola danych.',
'- scripts/plot_ntsc_english.py --video pal — wykresy.',
'- scripts/report_pal_isolated.py — ten raport.','',
'Zrzuty RAM i pełne logi są materiałami diagnostycznymi lokalnymi, nie przeznaczonymi do kopiowania do repozytorium.','']
(OUT/'RAPORT_PAL_PL.md').write_text('\n'.join(lines),encoding='utf-8')
print(OUT/'RAPORT_PAL_PL.md')
