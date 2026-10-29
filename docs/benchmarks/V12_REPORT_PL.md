# Pełny test FPS v12

310 nowych zimnych startów: 155 PAL i 155 NTSC, po 78 prosto i 77 z nurkowaniem. Cztery izolowane emulatory, nominalnie 60 s, domknięcie do pełnej prezentacji. Wynik 50/50 to połowa średniej każdego scenariusza. Oryginał i v11: zachowane pełne dane po 155 lotów na scenariusz/system.

![FPS](charts/V12_COMPARISON.png)

| System | Oryginał FPS | v11 FPS | v12 FPS | Zysk względem oryginału |
|---|---:|---:|---:|---:|
| PAL | 6.271731 | 8.782928 | 8.932929 | +42.4316% |
| NTSC | 5.591516 | 8.003108 | 8.149851 | +45.7539% |

### PAL

| Referencja | FPS referencji | Przyrost FPS | Zysk | Przedział 95% zysku |
|---|---:|---:|---:|---:|
| Original | 6.271731 | +2.661198 | +42.4316% | [+41.0787%, +43.7830%] |
| v11 full | 8.782928 | +0.150001 | +1.7079% | [+1.0790%, +2.3444%] |
| v11 matched 155 | 8.743560 | +0.189369 | +2.1658% | [+1.6135%, +2.6986%] |

v12 95% FPS interval: [8.854022, 9.011272]. Natural early ends: 8/155.

### NTSC

| Referencja | FPS referencji | Przyrost FPS | Zysk | Przedział 95% zysku |
|---|---:|---:|---:|---:|
| Original | 5.591516 | +2.558335 | +45.7539% | [+44.4038%, +47.0836%] |
| v11 full | 8.003108 | +0.146743 | +1.8336% | [+1.1732%, +2.4948%] |
| v11 matched 155 | 7.991736 | +0.158115 | +1.9785% | [+1.4598%, +2.4902%] |

v12 95% FPS interval: [8.080669, 8.218045]. Natural early ends: 9/155.

Czas serii: 20 min 15 s. Zachowano 17 naturalnych wcześniejszych zakończeń, bez odrzucania wyników. Zysk jest ilorazem średnich, nie średnią procentów. Przedziały: 20 000 replik bootstrapu, ziarno 2026102912, całe starty resamplowane w grupach 78/77. Historyczny oryginał prosto ma niezależny plan. Kontrola v11 matched korzysta z tych samych wybranych 155 prób co v12; pełna referencja v11 ma 310 lotów.

[Method](METHOD_PL.md) · [Build instructions](../REBUILD_PL.md) · [Data](../../results/v12/)

Nowy pomiar: `python scripts/benchmark_current.py --output results/new_v12`. Zainstaluj bridge w tools/bridge albo ustaw FRACTALUS_BRIDGE_DIR. Nie nadpisuj opublikowanych danych. `python scripts/report_v12.py` oraz `python scripts/plot_v12.py` odtwarzają statystyki i wykres.

ROM SHA-256: `4959a82ab36528a0448a40e6178fdb72d321e5d1e23c258036f5e22e51cfa20e`.
