from opt14_common import *
import argparse
p=argparse.ArgumentParser();p.add_argument('--base',default='v7_geometry');args=p.parse_args()
rom=bytearray((ROOT/f'build/{args.base}.rom').read_bytes())
code=assemble('v7_clipping','''; Exact common path; entered after signed x0<x1 comparison, C=0.
 opt h-
 org $8380
 cpx #0
 bne fallback
 lda $83
 ora $85
 ora $25d2
 ora $24e2
 bne fallback
 lda #20
 sta $9f
 lda $82
 cmp #216
 bcs done
 lda $84
 cmp #108
 bcc left_low
 lda $25f0
 cmp #108
 bcc right_low
 jmp $9788
left_low
 lda $25f0
 cmp #108
 bcc both_low
 jmp $972e
right_low
 jmp $974a
both_low
 jmp $9797
done
 rts
fallback
 clc
 lda $83
 bmi negative
 and #$1f
 jmp $9648
negative
 ora #$e0
 jmp $9648
 ert * > $84fd
''')
assert rom[0x563d:0x5640]==bytes.fromhex('a58330')
rom[0x563d:0x5640]=bytes.fromhex('4c8083');rom[0x4380:0x4380+len(code)]=code
meta=json.loads((ROOT/f'results/opt14/{args.base}-build.json').read_text());save('v7_clipping',rom,base=args.base,ram_patches=meta['ram_patches'])
