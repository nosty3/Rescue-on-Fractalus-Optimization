import pathlib, json, shutil, hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]; DEST=ROOT/'repository_backup'
m=json.loads((DEST/'docs/backup-manifest.json').read_text()); selected={x['path'] for x in m['files']}; selected.add('docs/backup-manifest.json')
def copy(src,dst=None):
    dst=dst or src; p=DEST/dst; p.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(ROOT/src,p); selected.add(dst)
for name in ('build_buffer_sync','test_buffer_sync','validate_buffer_sync','stress_buffer_sync','probe_buffer_race','detect_transient','release_v8','rebuild_v8','prepare_v8_backup'):
    copy(f'scripts/{name}.py')
copy('src/buffer_sync.asm'); copy('results/opt14/buffer_sync-build.json')
for p in (ROOT/'dist').glob('*v8*'): copy(p.relative_to(ROOT).as_posix())
for name in ('cpu-tests','sync-validation','stress','benchmark','final-summary'):
    copy(f'results/buffer_race/{name}.json')
copy('results/buffer_race/RAPORT_V8_PL.txt','docs/WYDANIE_V8_PL.txt')
summary=json.loads((ROOT/'results/buffer_race/final-summary.json').read_text()); fps=summary['fps']['buffer_sync']
p=DEST/'README_PL.md'; s=p.read_text(encoding='utf-8')
s=s.replace('Aktualne wydanie: v7','Aktualne wydanie: v8').replace('optimized v7 128KB.car','optimized v8 128KB.car').replace('rebuild_v7.py','rebuild_v8.py').replace('Raport bieżącego wydania: docs/WYDANIE_V7_PL.txt','Raport bieżącego wydania: docs/WYDANIE_V8_PL.txt')
notice=f'Bieżące v8: {fps:.6f} FPS (około +17,81% względem oryginału). Naprawia wyścig buforów powodujący jednoklatkowy klin po lewej. Wyniki v1–v7 poniżej są historyczne i nie oznaczają wersji wolnych od tego błędu.\n'
if notice not in s: s=s.replace('Wynik czterech lotów:',notice+'\nWynik czterech lotów:')
p.write_text(s,encoding='utf-8')
p=DEST/'docs/ODTWORZENIE_PL.md'; s=p.read_text(encoding='utf-8').replace('rebuild_v7.py','rebuild_v8.py').replace('wszystkich siedmiu ROM-ów','wszystkich ośmiu ROM-ów')
if 'v6, v7, v8' not in s: s=s.replace('v6, v7','v6, v7, v8')
p.write_text(s,encoding='utf-8')
updates={'KONTYNUACJA_PL.txt':f'AKTUALIZACJA v8 — NAPRAWA KLINÓW, {fps:.6f} FPS\nBank2 $9214 -> $84A0: osłona własności bufora, oczekiwanie na $42=0\nprzed czyszczeniem. Geometria nadal wykonuje się wcześniej.\nNie usuwać oczekiwania dla poprawy FPS. Raport: WYDANIE_V8_PL.txt.\nOdtworzenie: scripts/rebuild_v8.py. Zalecany zimny start CAR v8.\n', 'DALSZE_KIERUNKI_PL.txt':'AKTUALIZACJA v8 — SYNCHRONIZACJA WYŚWIETLANIA\nUtrzymywać test braku czyszczenia przed potwierdzeniem VBI ($42=0).\nTesty końcowego RAM nie wykrywają wszystkich błędów czasu wyświetlania.\nEwentualne ukrycie oczekiwania pracą bez zapisów do obrazu wymaga dowodu\nrozłączności danych i zysku >=0,05 FPS. Trzeci bufor wymaga analizy RAM\ni ANTIC; dodatkowy ROM sam nie wystarczy. Tych pomysłów nie wdrożono.\nPunkty 5–8 wcześniejszego audytu pozostają odłożone.\n'}
for name,prefix in updates.items():
    p=DEST/'docs'/name; s=p.read_text(encoding='utf-8')
    if not s.startswith(prefix): p.write_text(prefix+'\n'+s,encoding='utf-8')
rec=DEST/'build/reconstruction-v8.json'
if rec.exists():
    assert json.loads(rec.read_text())['result']=='pass'; copy('repository_backup/build/reconstruction-v8.json','results/buffer_race/reconstruction-v8.json')
records=[]
for name in sorted(selected):
    if name=='docs/backup-manifest.json': continue
    d=(DEST/name).read_bytes(); records.append({'path':name,'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest(),'git_blob_sha':hashlib.sha1(b'blob '+str(len(d)).encode()+b'\0'+d).hexdigest()})
m['files']=records; m['current_release']='v8'; m['v8_reconstruction_verified']=rec.exists()
(DEST/'docs/backup-manifest.json').write_text(json.dumps(m,indent=2),encoding='utf-8')
(ROOT/'v8_backup_selected.json').write_text(json.dumps(sorted(selected)))
print('Selected',len(selected),'files; v8 rebuilt',rec.exists())
