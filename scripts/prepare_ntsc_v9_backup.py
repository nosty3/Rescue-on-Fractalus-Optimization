import pathlib,json,hashlib,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1];DEST=ROOT/'repository_backup'
m=json.loads((DEST/'docs/backup-manifest.json').read_text());selected={x['path'] for x in m['files']}
def copy(src,dst=None):
 dst=dst or src;p=DEST/dst;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/src,p);selected.add(dst)
for name in ('ntsc_v9_common','prepare_ntsc_v9','benchmark_ntsc_v9','stress_ntsc_v9','validate_ntsc_v9','visual_ntsc_v9','report_ntsc_v9','prepare_ntsc_v9_backup'):copy(f'scripts/{name}.py')
for name in ('preparation','benchmark','stress','validation','visual-controls','summary'):copy(f'results/ntsc_v9/{name}.json')
copy('results/ntsc_v9/POMIAR_NTSC_V9_PL.md','docs/POMIAR_NTSC_V9_PL.md')
records=[]
for name in sorted(selected):
 if name=='docs/backup-manifest.json':continue
 d=(DEST/name).read_bytes();records.append({'path':name,'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest(),'git_blob_sha':hashlib.sha1(b'blob '+str(len(d)).encode()+b'\0'+d).hexdigest()})
m['files']=records;m['v9_ntsc_tested']='2026-10-22';(DEST/'docs/backup-manifest.json').write_text(json.dumps(m,indent=2),encoding='utf-8');print('Selected',len(records)+1,'files; existing names and READMEs unchanged')
