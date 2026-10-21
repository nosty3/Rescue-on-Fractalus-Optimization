from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=(ROOT/'scripts/stress_buffer_sync.py').read_text().replace("name='buffer_sync'","name='pmg_trial'").replace('results/buffer_race/','results/pmg_trial/')
(ROOT/'scripts/stress_pmg_trial.py').write_text(s)
