"""Human-readable pilot/main report and plots from saved completed samples."""
from pathlib import Path
import argparse,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('stage',choices=['pilot','main']);args=p.parse_args()
OUT=ROOT/f'results/ntsc_isolated_{args.stage}'
d=json.loads((OUT/'benchmark.json').read_text());s=json.loads((OUT/'summary.json').read_text())
n=d['metadata']['count_per_version'];rows=d['rows']
amended=(OUT/'UZUPELNIENIE_PROTOKOLU_PL.md').exists()
def f(x,k=4):return f'{x:.{k}f}'.replace('.',',')
lines=[f"# NTSC: {'pilot' if args.stage=='pilot' else 'pomiar główny'} — świeży proces dla każdej próby",'',
f'{n} natywnych startów oryginału i {n} natywnych startów v9. Żadnych zapisów stanu ani modyfikacji pamięci gry. '
'Pomiary 15, 30 i 60 s są zagnieżdżone w tym samym locie; jednostką statystyczną jest cały lot.', '',
'## Warunki i populacja scenariuszy','',
'Atari 800XL 64 KB NTSC, standardowa konfiguracja bez przyspieszaczy, domyślny poziom, joystick wycentrowany, '
'bez dopalacza i strzelania. START po 3000–3599 klatkach wideo od BOOT. '
'Czasy losowane jednostajnie bez powtórzeń osobno dla każdej wersji; nie gwarantuje to jednostajnego rozkładu wszystkich map gry. '
'Każde 5 prób każdej wersji tworzy zrównoważony blok, kolejność wewnątrz bloku losowa. '
'Harmonogram i liczba prób zapisane w plan.json przed rozpoczęciem.', '',
'Po pierwszym wejściu $A32E zwalniamy START i wykonujemy 170 klatek wideo rozgrzewki. '
'Następnie mierzymy liczbę odstępów pomiędzy ukończonymi obrazami na $B516 i ich czas w taktach Atari '
'(1 789 772,5 Hz). Domykamy pierwszy pełny odstęp po 15/30/60 s. '
    'Wszystkie zliczone ukończenia obrazów należą do trybu lotu 2. '
'Zapisujemy pełne odstępy, hashe terenu, pamięć przy wejściu i konfigurację.', '',
'Wyniki opisują średnią z jawnie zdefiniowanego zbioru 600 możliwych momentów START dla każdej wersji '
'w tym emulatorze i scenariuszu. Nie opisują automatycznie wszystkich poziomów, sprzętów i sposobów grania. '
'Nie dobieramy map pod korzystny wynik ani nie usuwamy poprawnych skrajnych prób.', '',
'Porównujemy natywne uruchomienia obu wersji przy tym samym rozkładzie momentów START. '
'Nie wymuszamy jednakowych map: audyt wykazał, że ten sam moment START może generować różny teren '
'w oryginale i v9. Procentowy zysk dotyczy średniego wyniku tego scenariusza użytkowego; '
'nie jest izolowanym pomiarem przyspieszenia renderera na identycznym terenie.', '',
'## Średnie i rozrzut', '',
'| Okno | Oryginał FPS | SD oryginału | v9 FPS | SD v9 | Zysk |',
'|---|---:|---:|---:|---:|---:|']
for sec,g in s['windows'].items():
    lines.append(f"| {sec} s | {f(g['original']['mean'])} | {f(g['original']['sd'])} | {f(g['v9']['mean'])} | {f(g['v9']['sd'])} | +{f(g['gain_percent'],2)}% |")
g=s['windows']['60']
lines+=['','## Niepewność wyniku 60 s','']
for v in ('original','v9'):
    q=g[v]
    lines.append(f"- {v}: średnia {f(q['mean'])} FPS, orientacyjny przedział ufności 95% {f(q['mean_ci95'][0])}–{f(q['mean_ci95'][1])} FPS; różne tablice terenu {q['unique_maps']}/{n}.")
    lines.append(f"- {v}: loty zakończone przed limitem 60 s: {q['shortened_flights']}/{n}; zakres rzeczywistych czasów mierzonych odstępów: {f(q['measured_seconds_range'][0],3)}–{f(q['measured_seconds_range'][1],3)} s.")
ci=g['gain_delta_normal_ci95'];cb=g['gain_stratified_bootstrap_ci95']
lines += ['',f"Kontrola sposobu uśredniania: suma wszystkich ukończonych odstępów / suma ich czasów daje {f(g['original']['pooled_fps'])} FPS dla oryginału i {f(g['v9']['pooled_fps'])} FPS dla v9, czyli +{f(g['pooled_gain_percent'],2)}%. "
    'To wynik ważony długością lotu; główny wynik powyżej nadaje każdemu wylosowanemu lotowi jednakową wagę.', '']
lines += [f"- Zysk: +{f(g['gain_percent'],2)}%; przybliżony przedział 95% metodą propagacji wariancji {f(ci[0],2)}%–{f(ci[1],2)}% (połowa szerokości {f((ci[1]-ci[0])/2,2)} p.p.).",
f"- Kontrola bootstrap: {f(cb[0],2)}%–{f(cb[1],2)}%. Losowano całe loty wewnątrz każdej kombinacji blok/wariant, zachowując liczebność bloków. 50 000 replikacji; nie losowano pojedynczych klatek.", '',
'Przedziały są przybliżone i warunkowe dla tego planu próbkowania. W wariancie analitycznym nie zastosowano '
'korekty na skończony zbiór 600 scenariuszy, co daje zachowawcze oszacowanie błędu losowania bez zwracania. '
'Bootstrap utrzymuje zaobserwowane bloki, nie modeluje nieznanych wspólnych zmian między przyszłymi sesjami. '
'Powtarzalność techniczną sprawdzono osobnym audytem; wynik audytu nie jest dowodem pełnej poprawności emulatora.', '',
'## Bloki 60 s', '', '| Blok | Oryginał FPS | v9 FPS | Zysk |', '|---|---:|---:|---:|']
for b,bg in s['blocks'].items():lines.append(f"| {b} | {f(bg['original'])} | {f(bg['v9'])} | +{f(bg['gain_percent'],2)}% |")
lines+=['','## Zależność od długości lotu i kolejności','']
lines+=['Kolejność w poniższej diagnostyce oznacza pozycję w zamrożonym harmonogramie. Przy wykonaniu równoległym nie jest to ścisła kolejność rozpoczęcia ani zakończenia procesów.', '']
for v,q in s['stability'].items():
    lines.append(f"- {v}: SD dla 60 s / SD dla 15 s = {f(q['sd_ratio_60_to_15'],3)}; korelacja kolejność–FPS rho={f(q['order_spearman']['rho'],3)}, p={f(q['order_spearman']['p'],3)}; test Kruskala między blokami p={f(q['kruskal_blocks_p'],3)}.")
lines+=['','Wyniki diagnostycznych testów nie są dowodem równoważności bloków. Zmiana średniej przy dłuższym '
'locie może wynikać z innego obciążenia na dalszej części trasy; 60 s nie jest wyłącznie dokładniejszym '
'oszacowaniem tego samego pierwszego odcinka 15 s.','']
if args.stage=='main':
    lines+=['W v9 test różnic między blokami daje niekorygowane p≈0,040. Jest to sygnał diagnostyczny '
        'z kilku wykonywanych porównań, nie dowód dryfu emulatora ani identyczności małych serii. '
        'Bloki zawierają różne losowo przypisane scenariusze. Nie zaobserwowano istotnej monotonicznej '
        'zależności od pozycji w harmonogramie; nie wyklucza to innych różnic. Podany główny przedział '
        'opisuje losowanie z ustalonej populacji scenariuszy, a nie nieznane zmiany między emulatorami lub sesjami.', '']
if args.stage=='pilot':
    q=s['planning']
    lines+=['## Planowanie oddzielnego pomiaru głównego','',
    f"Dla celu ±1 p.p. zysku (95%) i zaobserwowanego rozrzutu 60 s: około {q['normal_approx_n_per_version']} prób na wersję. "
    f"Z 20% zapasem i zaokrągleniem do pełnych bloków: {q['proposed_fixed_n_per_version']} prób na wersję.", '',
    'To prognoza, nie gwarancja końcowej dokładności. Liczbę należy zamrozić przed pomiarem głównym; '
    'nie kończyć go na podstawie korzystnego chwilowego wyniku. Pilota nie dodawać do średniej potwierdzającego testu.', '']
else:
    half=(ci[1]-ci[0])/2
    lines+=['## Ocena zaplanowanej dokładności','',
    f"Cel ±1 p.p. {'osiągnięty' if half<=1 else 'nieosiągnięty'} według zastosowanego przybliżonego przedziału: ±{f(half,2)} p.p. "
    'Nie dobierano dodatkowych prób po obejrzeniu wyniku i nie dołączono danych pilota.', '']
lines+=['## Materiały','', '- `plan.json`: zapisany z góry harmonogram.', '- `benchmark.json`: wszystkie wyniki i metadane.',
'- `summary.json`: statystyki.', '- `scripts/benchmark_ntsc_isolated.py`: procedura pomiarowa.',
'- `scripts/summarize_ntsc_isolated.py`: obliczenia.', '- `scripts/report_ntsc_isolated.py`: raport i wykres.',
'', 'Pomocniczych zrzutów RAM, pełnych logów emulatora i list taktów nie należy publikować w repozytorium.', '']
(OUT/'RAPORT_NTSC_PL.md').write_text('\n'.join(lines),encoding='utf-8')
if amended:
    note=['**Uwaga o definicji wyniku:** po 47 ukończonych próbach napotkano naturalne zakończenie lotu przed minutą. '
        'Procedurę jawnie uzupełniono: próba trwa do limitu 60 s albo do końca lotu, a krótsze loty pozostają w średniej. '
        'Nie doliczamy animacji końca gry. Nie jest to średnia wyłącznie z pełnych minut. '
        'Regułę dopisano w toku badania; szczegóły w UZUPELNIENIE_PROTOKOLU_PL.md. '
        'Liczebność i harmonogram nie zmieniły się. Wynik nie jest testem w całości zarejestrowanym z góry dla tej uzupełnionej definicji.', '']
    lines[2:2]=note
    lines += ['', '## Zmiana sposobu wykonania', '',
        'Pierwsze 86 prób wykonano sekwencyjnie. Po zgodzie użytkownika i dokładnej walidacji czterech lotów '
        '(minimum i maksimum FPS pilota dla każdej wersji) pozostałe próby wykonano w maksymalnie czterech '
        'oddzielnych emulatorach. Walidacja obejmowała wszystkie odstępy między obrazami, punkty 15/30/60 s '
        'i pełne 32 KB RAM w trzech punktach; uzyskano pełną zgodność. '
        'Nie zmieniono zaplanowanych scenariuszy. Szczegóły: ../ntsc_parallel_validation/WALIDACJA_PL.md.', '']
    (OUT/'RAPORT_NTSC_PL.md').write_text('\n'.join(lines),encoding='utf-8')

fig,axes=plt.subplots(1,2,figsize=(13,6),dpi=160)
fig.patch.set_facecolor('#f8fafc')
for ax,v,title,color in zip(axes,('original','v9'),('Oryginał','v9'),('#2563a6','#e78125')):
    values=np.array([[r['measurement']['checkpoints'][sec]['fps'] for sec in ('15','30','60')] for r in rows if r['variant']==v])
    for yy in values:ax.plot([15,30,60],yy,color=color,alpha=.18,lw=.8)
    ax.plot([15,30,60],values.mean(axis=0),color=color,lw=3,marker='o',label='Średnia')
    ax.set_title(title);ax.set_xticks([15,30,60]);ax.set_xlabel('Limit czasu pomiaru [s]');ax.set_ylabel('Średni FPS od początku okna')
    ax.grid(alpha=.2);ax.legend();ax.spines[['top','right']].set_visible(False)
fig.suptitle(f'NTSC · {args.stage} · {n} lotów każdej wersji',fontsize=18,fontweight='bold')
fig.text(.08,.03,'Cienka linia: jeden lot; okna są zależne. Loty zakończone wcześniej zachowują wynik do chwili końca lotu.' if amended else 'Cienka linia: jeden lot. Punkty 15/30/60 s są zależne — to kolejne okna tego samego przebiegu.',fontsize=9)
fig.subplots_adjust(top=.86,bottom=.17,wspace=.23)
fig.savefig(OUT/'DLUGOSC_LOTU_NTSC_PL.png',facecolor=fig.get_facecolor())
plt.close(fig)
fig,axes=plt.subplots(1,2,figsize=(12,5),dpi=160)
colors={'original':'#2563a6','v9':'#e78125'}
allfps=[r['measurement']['checkpoints']['60']['fps'] for r in rows]
bins=np.linspace(min(allfps)-.05,max(allfps)+.05,24)
for v,label in (('original','Oryginał'),('v9','v9')):
    x=np.array([r['measurement']['checkpoints']['60']['fps'] for r in rows if r['variant']==v])
    axes[0].hist(x,bins=bins,alpha=.55,color=colors[v],label=label)
    axes[0].axvline(x.mean(),color=colors[v],ls='--',lw=2)
    axes[1].step(np.sort(x),np.arange(1,len(x)+1)/len(x),where='post',color=colors[v],lw=2,label=label)
axes[0].set(title='Rozkład FPS poszczególnych lotów',xlabel='FPS',ylabel='Liczba lotów')
axes[1].set(title='Dystrybuanta empiryczna',xlabel='FPS',ylabel='Udział lotów o FPS nie większym niż x')
for ax in axes:
    ax.legend();ax.grid(alpha=.2);ax.spines[['top','right']].set_visible(False)
fig.suptitle(f'NTSC · {n} natywnych startów każdej wersji · limit 60 s',fontsize=15)
fig.text(.08,.02,'Bez usuwania skrajnych wyników. Linie przerywane: średnie. Każdy lot ma jednakową wagę.',fontsize=9)
fig.tight_layout(rect=(0,.05,1,.93))
fig.savefig(OUT/'ROZKLAD_NTSC_PL.png')
print(OUT/'RAPORT_NTSC_PL.md')
