import pathlib,json,shutil,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1];DEST=ROOT/'repository_backup';m=json.loads((DEST/'docs/backup-manifest.json').read_text());selected={x['path'] for x in m['files']};selected.add('docs/backup-manifest.json')
def copy(src,dst=None):
 dst=dst or src;p=DEST/dst;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/src,p);selected.add(dst)
for pattern in ('src/v7_*.asm','scripts/build_v7_*.py','scripts/test_v7_*.py','scripts/research_v6_*.py'):
 for p in ROOT.glob(pattern):copy(p.relative_to(ROOT).as_posix())
for name in ('probe_v7_geometry','prepare_v7_checks','stress_v7','release_v7','rebuild_v7','prepare_v7_backup'):copy(f'scripts/{name}.py')
for p in (ROOT/'dist').glob('*v7*'):copy(p.relative_to(ROOT).as_posix())
for name in ('profile-manifest','summary','clipping-tests','geometry-live-probe','candidate-estimates','integration-tests','stress','benchmark','final-summary'):copy(f'results/research_v6/{name}.json')
for name in ('v7-geometry-tests','v7_geometry-build','v7_clipping-build'):copy(f'results/opt14/{name}.json')
counts=json.loads((ROOT/'results/research_v6/clipping-census.json').read_text())['counts'];p=DEST/'results/research_v6/clipping-census-summary.json';p.write_text(json.dumps({'counts':counts,'fixtures':58},indent=2));selected.add(p.relative_to(DEST).as_posix())
copy('results/research_v6/RAPORT_V7_PL.txt','docs/WYDANIE_V7_PL.txt')
p=DEST/'README_PL.md';s=p.read_text(encoding='utf-8').replace('Aktualne wydanie: v6','Aktualne wydanie: v7').replace('v6 7,691000 FPS. Zysk v6: 17,36% względem oryginału, 4,39% względem v5.','v6 7,691000; v7 7,883239 FPS. Zysk v7: 20,29% względem oryginału, 2,50% względem v6.').replace('optimized v6 128KB.car','optimized v7 128KB.car').replace('rebuild_v6.py','rebuild_v7.py').replace('Raport bieżącego wydania: docs/WYDANIE_V6_PL.txt','Raport bieżącego wydania: docs/WYDANIE_V7_PL.txt');p.write_text(s,encoding='utf-8')
p=DEST/'docs/ODTWORZENIE_PL.md';s=p.read_text(encoding='utf-8').replace('rebuild_v6.py','rebuild_v7.py').replace('wszystkich sześciu ROM-ów','wszystkich siedmiu ROM-ów')
if 'buduje v1, v2, v3, v4, v5, v6, v7' not in s:s=s.replace('buduje v1, v2, v3, v4, v5, v6','buduje v1, v2, v3, v4, v5, v6, v7')
p.write_text(s,encoding='utf-8')
updates={'KONTYNUACJA_PL.txt':'AKTUALIZACJA v7 — wynik 7,883239 FPS, patrz WYDANIE_V7_PL.txt.\nBanki 10..13: rozwinięte ogony geometrii i tabele $9D00/$9E00; $9F\njest zachowany na stosie i przywracany. Wejście/wyjście banków bez zmian.\nBank2 $963D skacze do szybkiego obcinania $8380 (dawny interpreter).\nPrzy breakpointach i testach CPU rozróżniać PC wraz z bankiem.\nOdtworzenie offline: scripts/rebuild_v7.py.\n','DALSZE_KIERUNKI_PL.txt':'AKTUALIZACJA v7 / PRÓG 0,05 FPS\nWdrożono dalszą specjalizację geometrii (+0,1162 FPS) oraz szybkie\nobcinanie (+0,0760 FPS). Pozostałe sprawdzone drobne pomysły poniżej\n0,05 FPS odrzucono; patrz WYDANIE_V7_PL.txt i candidate-estimates.json.\nPunkty 5..8 wcześniejszego audytu nadal odłożone. Cache między klatkami\nnie ma wykazanego kontraktu poprawności ani wiarygodnego budżetu zysku.\nNie ogłaszamy absolutnego optimum; dalsza implementacja wymaga nowego\nkandydata z uzasadnionym zyskiem >=0,05 FPS i zachowaniem wyników gry.\n'}
for name,prefix in updates.items():
 p=DEST/'docs'/name;s=p.read_text(encoding='utf-8')
 if not s.startswith(prefix):p.write_text(prefix+'\n'+s,encoding='utf-8')
rec=DEST/'build/reconstruction-v7.json'
if rec.exists():
 assert json.loads(rec.read_text())['result']=='pass';copy('repository_backup/build/reconstruction-v7.json','results/research_v6/reconstruction-v7.json')
records=[]
for name in sorted(selected):
 if name=='docs/backup-manifest.json':continue
 d=(DEST/name).read_bytes();records.append({'path':name,'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest(),'git_blob_sha':hashlib.sha1(b'blob '+str(len(d)).encode()+b'\0'+d).hexdigest()})
m['files']=records;m['current_release']='v7';m['v7_reconstruction_verified']=rec.exists();(DEST/'docs/backup-manifest.json').write_text(json.dumps(m,indent=2),encoding='utf-8');(ROOT/'v7_backup_selected.json').write_text(json.dumps(sorted(selected)));print('Selected',len(selected),'files; v7 rebuilt',rec.exists())
