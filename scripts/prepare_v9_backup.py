import pathlib,json,hashlib,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1];DEST=ROOT/'repository_backup'
m=json.loads((DEST/'docs/backup-manifest.json').read_text());selected={x['path'] for x in m['files']};selected.add('docs/backup-manifest.json')
def copy(src,dst=None):
 dst=dst or src;p=DEST/dst;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/src,p);selected.add(dst)
for name in ('audit_pmg','probe_pmg','probe_pmg_special','export_pmg_listing','build_pmg_trial','test_pmg_trial','validate_pmg_trial','prepare_pmg_checks','stress_pmg_trial','report_pmg_trial','check_pmg_initialization','release_v9','rebuild_v9','prepare_v9_backup'):copy(f'scripts/{name}.py')
for name in ('pmg_short_loops','pmg_bar_delta'):copy(f'src/{name}.asm')
for name in ('cpu-tests','bar-invariant','initialization','stress','benchmark','summary','release-v9'):copy(f'results/pmg_trial/{name}.json')
for name in ('cpu-observations','live-input-observations','special-paths'):copy(f'results/pmg_audit/{name}.json')
for name in ('AUDYT_PMG_PL.md','PROCEDURY_PMG_PL.txt'):copy('results/pmg_audit/'+name,'docs/'+name)
for name in ('PROBA_PMG_PL.md','WYDANIE_V9_PL.md'):copy('results/pmg_trial/'+name,'docs/'+name)
copy('results/opt14/pmg_trial-build.json')
for p in (ROOT/'dist').glob('*v9*'):copy(p.relative_to(ROOT).as_posix())
p=DEST/'README_PL.md';s=p.read_text(encoding='utf-8').replace('Aktualne wydanie: v8','Aktualne wydanie: v9').replace('optimized v8 128KB.car','optimized v9 128KB.car').replace('rebuild_v8.py','rebuild_v9.py').replace('Raport bieżącego wydania: docs/WYDANIE_V8_PL.txt','Raport bieżącego wydania: docs/WYDANIE_V9_PL.md')
s=s.replace('Bieżące v8: 7.720697 FPS (około +17,81% względem oryginału). Naprawia wyścig buforów powodujący jednoklatkowy klin po lewej.','Bieżące v9: 7,764418 FPS. Mała optymalizacja PMG: +0,043721 FPS względem v8 (7,720697 FPS), zaakceptowana przez użytkownika mimo progu +0,05 FPS. Zachowuje naprawę wyścigu buforów z v8.')
p.write_text(s,encoding='utf-8')
p=DEST/'docs/ODTWORZENIE_PL.md';s=p.read_text(encoding='utf-8').replace('rebuild_v8.py','rebuild_v9.py').replace('wszystkich ośmiu ROM-ów','wszystkich dziewięciu ROM-ów')
if 'v7, v8, v9' not in s:s=s.replace('v7, v8','v7, v8, v9')
p.write_text(s,encoding='utf-8')
updates={'KONTYNUACJA_PL.txt':'AKTUALIZACJA v9 — PMG, 7,764418 FPS\nPasek różnicowy: fallback pełnego odrysowania przy starej wartości 0.\nHelpery w banku 2: $83CA..$8470 i $84B0..$84F3. Wywołania z VBI.\nOsłona buforów v8 pozostaje. Odtworzenie: scripts/rebuild_v9.py.\nRaport: WYDANIE_V9_PL.md. Zalecany zimny start CAR v9.\n','DALSZE_KIERUNKI_PL.txt':'AKTUALIZACJA v9 — przyjęto pierwszą próbę PMG\nZysk +0,043721 FPS przyjęty na wyraźną prośbę użytkownika jako wyjątek\nod progu +0,05. Pozostałe pomysły PMG pozostają w AUDYT_PMG_PL.md.\nNie rozszerzono implementacji na renderer RAM, RANDOM ani przewijanie.\n'}
for name,prefix in updates.items():
 p=DEST/'docs'/name;s=p.read_text(encoding='utf-8')
 if not s.startswith(prefix):p.write_text(prefix+'\n'+s,encoding='utf-8')
rec=DEST/'build/reconstruction-v9.json'
if rec.exists():
 assert json.loads(rec.read_text())['result']=='pass';copy('repository_backup/build/reconstruction-v9.json','results/pmg_trial/reconstruction-v9.json')
records=[]
for name in sorted(selected):
 if name=='docs/backup-manifest.json':continue
 d=(DEST/name).read_bytes();records.append({'path':name,'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest(),'git_blob_sha':hashlib.sha1(b'blob '+str(len(d)).encode()+b'\0'+d).hexdigest()})
m['files']=records;m['current_release']='v9';m['v9_reconstruction_verified']=rec.exists();(DEST/'docs/backup-manifest.json').write_text(json.dumps(m,indent=2),encoding='utf-8')
print('Selected',len(selected),'files; v9 rebuilt',rec.exists())
