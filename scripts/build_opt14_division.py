from opt14_common import *
rom=bytearray((ROOT/'dist/Rescue on Fractalus! - PAL optimized v5 128KB.rom').read_bytes())
save('opt14_base',rom)
assert rom[0x4224:0x4229]==bytes.fromhex('8a484c3182')
code=assemble('opt14_division','''; Quotient-only contract, N < D < 32768, D=0 processor mode.
; AE/AF and B0/B1 are scratch and are not normalized on return.
 opt h-
 org $8224
 txa
 pha
 jmp $8235
''')
rom[0x4224:0x4224+len(code)]=code
save('opt14_division',rom,base='opt14_base',scratch_changed=[0xae,0xaf,0xb0,0xb1])
