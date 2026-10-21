from opt14_common import *
rom=bytearray((ROOT/'build/buffer_sync.rom').read_bytes())
def fixed(at,old,new):
 p=len(rom)-8192+at-0xa000
 old=bytes.fromhex(old); assert rom[p:p+len(old)]==old,(hex(at),rom[p:p+len(old)].hex()); rom[p:p+len(new)]=new
source=' opt h-\n org $83ca\ncopy21\n'
source+=(' iny\n lda $afce,x\n sta $0e87,y\n inx\n'*3)+' dec $bd\n bne copy21\n jmp $a556\n'
source+='clear5\n'+(' sta $0f98,y\n iny\n'*5)+' ldx #0\n jmp $a8f1\n'
source+='draw5\n'+(' lda $a93e,x\n sta $0f98,y\n inx\n iny\n'*5)+' lda #0\n sta $bb\n jmp $a92a\n'
for label,op,target in [('clear3','and #$cf','$a971'),('draw3','ora #$30','$a981')]:
 source+=label+'\n'+(f' lda $0b91,y\n {op}\n sta $0b91,y\n iny\n'*3)+f' ldx #0\n jmp {target}\n'
source+=' ert * > $84a0\n'
code=assemble('pmg_short_loops',source);rom[0x43ca:0x43ca+len(code)]=code
# Labels from assembler listing, independently computed from emitted lengths.
labels={'copy21':0x83ca,'clear5':0x83ca+31,'draw5':0x83ca+31+25,'clear3':0x83ca+31+25+47,'draw3':0x83ca+31+25+47+32}
for at,label in [(0xa54a,'copy21'),(0xa8ea,'clear5'),(0xa91e,'draw5'),(0xa965,'clear3'),(0xa975,'draw3')]:
 p=len(rom)-8192+at-0xa000; target=labels[label]; rom[p:p+3]=bytes([0x4c,target&255,target>>8])
fixed(0xa547,'15',bytes([7]))
delta=''' opt h-
 org $84b0
 tya
 cmp #56
 bcs fallback
 lda $2875
 beq fallback
 cmp #56
 bcs fallback
 txa
 pha
 ldx $2875
 tya
 cmp $2875
 sty $2875
 bcc decrease
 lda #0
increase
 inx
 sta $0c97,x
 cpx $2875
 bne increase
 beq done
decrease
 lda #$ff
fill
 sta $0c97,x
 dex
 cpx $2875
 bne fill
done
 pla
 tax
 ldy #56
 lda #$ff
 sec
 jmp $a57c
fallback
 sty $2875
 jmp $a567
 ert * > $84fd
'''
code=assemble('pmg_bar_delta',delta);rom[0x44b0:0x44b0+len(code)]=code
fixed(0xa564,'8c7528',bytes.fromhex('4cb084'))
meta=json.loads((ROOT/'results/opt14/buffer_sync-build.json').read_text())
save('pmg_trial',rom,base='buffer_sync',ram_patches=meta['ram_patches'],labels=labels)
