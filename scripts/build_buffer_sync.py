from opt14_common import *
rom=bytearray((ROOT/'build/v7_clipping.rom').read_bytes())
code=assemble('buffer_sync','''; Do not clear the previously displayed buffer until VBI acknowledges.
; Geometry can still run ahead. Preserve the complete caller register state.
 opt h-
 org $84a0
 php
 pha
 lda $4a
 beq ready
wait_present
 lda $42
 bne wait_present
ready
 pla
 plp
 jmp $982f
 ert * > $84fd
''')
assert rom[0x5214:0x5217]==bytes.fromhex('4c2f98');rom[0x5214:0x5217]=bytes.fromhex('4ca084');rom[0x44a0:0x44a0+len(code)]=code
meta=json.loads((ROOT/'results/opt14/v7_clipping-build.json').read_text());save('buffer_sync',rom,base='v7_clipping',ram_patches=meta['ram_patches'])
