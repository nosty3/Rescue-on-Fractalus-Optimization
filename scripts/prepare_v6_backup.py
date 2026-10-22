import pathlib,json,shutil,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1];DEST=ROOT/'repository_backup'
m=json.loads((DEST/'docs/backup-manifest.json').read_text());selected={x['path'] for x in m['files']};selected.add('docs/backup-manifest.json')
def copy(src,dst=None):
 dst=dst or src;p=DEST/dst;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/src,p);selected.add(dst)
for pattern in ('src/opt14_*.asm','scripts/build_opt14_*.py','scripts/test_opt14_*.py'):
 for p in ROOT.glob(pattern):copy(p.relative_to(ROOT).as_posix())
for name in ('opt14_common','opt14_cpu','benchmark_opt14','probe_opt14_geometry','stress_opt14','tune_opt14_width45','release_opt14','rebuild_v6','prepare_v6_backup'):
 copy(f'scripts/{name}.py')
for p in (ROOT/'dist').glob('*v6*'):copy(p.relative_to(ROOT).as_posix())
for name in ('benchmark','division-tests','division-vbi-tests','geometry-live-probe','geometry-tests','interpolation-tests','integration-tests','stress','opt14_base-build','opt14_division-build','opt14_width45-build','opt14_geometry-build','opt14_interpolation-build','opt14_width45-renderer-tests','rejected-geometry-layout','width45-random','width45-tuning','final-summary'):
 copy(f'results/opt14/{name}.json')
copy('results/opt14/RAPORT_V6_PL.txt','docs/WYDANIE_V6_PL.txt')
p=DEST/'README_PL.md';s=p.read_text(encoding='utf-8').replace('Aktualne wydanie: v5','Aktualne wydanie: v6').replace('v5 7,367256 FPS. Zysk v5: 12,42% względem oryginału, 0,69% względem v4.','v5 7,367256; v6 7,691000 FPS. Zysk v6: 17,36% względem oryginału, 4,39% względem v5.').replace('optimized v5 128KB.car','optimized v6 128KB.car').replace('rebuild_v5.py','rebuild_v6.py').replace('Nowy audyt v5, bez wdrożenia poprawek:','Historyczny audyt v5 (punkty 1–4 wdrożone w v6, 5–8 odłożone):').replace('Raport bieżącego wydania: docs/WYDANIE_V5_PL.txt','Raport bieżącego wydania: docs/WYDANIE_V6_PL.txt');p.write_text(s,encoding='utf-8')
p=DEST/'docs/ODTWORZENIE_PL.md';s=p.read_text(encoding='utf-8').replace('rebuild_v5.py','rebuild_v6.py').replace('wszystkich pięciu ROM-ów','wszystkich sześciu ROM-ów')
if 'buduje v1, v2, v3, v4, v5, v6' not in s:s=s.replace('buduje v1, v2, v3, v4, v5','buduje v1, v2, v3, v4, v5, v6')
p.write_text(s,encoding='utf-8')
updates={
'KONTYNUACJA_PL.txt':'AKTUALIZACJA v6: raport WYDANIE_V6_PL.txt, wynik 7,691000 FPS.\nPunkty 1–4 wdrożone. Banki 10..13: stałe komendy geometrii; bank14:\ninterpolacja tablicowa; RAM $7EEB..$7FC1 zawiera nowy kod i osiem operandów\nSMC. Osłona VBI akceptuje znaczniki <15. Stare save-state wymagają podmiany\nkodu RAM przez opt14_common.patch_state(); zimny start ładuje go z ROM.\nZapasowa ścieżka czyszczenia $921A..$9307 musi pozostać nienaruszona.\nTesty CPU korzystają z opt14_cpu.py, który odrzuca nieobsługiwane opcodes.\nOdtworzenie bez fixture/SDK: scripts/rebuild_v6.py.\n',
'DALSZE_KIERUNKI_PL.txt':'DECYZJA UŻYTKOWNIKA / v6 — 21.10.2026\nPunkty 1–4 audytu OPCJE_OPTYMALIZACJI_V5_PL.md wykonane i sprawdzone.\nPunkty 5–8 odłożone: wyrównanie stron; mnożenie $7CD6; kanały dźwięku;\npierwszy wiersz wypełniania 33–48. Nie wdrażamy ich, pozostają opisane\nw historycznym audycie wraz z wstępnymi szacunkami.\nNie ma już pustych banków 10..14, są zajęte przez v6. Dalsza praca wymaga\nnowego pomiaru i decyzji użytkownika; dawnych prognoz nie sumować z v6.\n'}
for name,prefix in updates.items():
 p=DEST/'docs'/name;s=p.read_text(encoding='utf-8')
 if not s.startswith(prefix):p.write_text(prefix+'\n'+s,encoding='utf-8')
reconstruction=DEST/'build/reconstruction-v6.json'
if reconstruction.exists():
 data=json.loads(reconstruction.read_text());assert data['result']=='pass';copy('repository_backup/build/reconstruction-v6.json','results/opt14/reconstruction-v6.json')
records=[]
for name in sorted(selected):
 if name=='docs/backup-manifest.json':continue
 d=(DEST/name).read_bytes();records.append({'path':name,'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest(),'git_blob_sha':hashlib.sha1(b'blob '+str(len(d)).encode()+b'\0'+d).hexdigest()})
m['files']=records;m['current_release']='v6';m['v6_reconstruction_verified']=reconstruction.exists();(DEST/'docs/backup-manifest.json').write_text(json.dumps(m,indent=2),encoding='utf-8')
(ROOT/'v6_backup_selected.json').write_text(json.dumps(sorted(selected)))
print('Selected',len(selected),'files; reconstruction',reconstruction.exists())
