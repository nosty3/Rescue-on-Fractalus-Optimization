from session import *
def patch_loaded_state(a):
 meta=json.loads((ROOT/'results/lowlevel/full-build.json').read_text())
 code=bytes.fromhex(meta['ram_patch_hex']);at=meta['ram_patch_address']
 old=(ROOT/'tests/fixtures/center-0.bin').read_bytes()[at:at+len(code)]
 assert a.peek(at,len(code)) in (old,code)
 for i,value in enumerate(code):a.poke(at+i,value)
 assert a.peek(at,len(code))==code
