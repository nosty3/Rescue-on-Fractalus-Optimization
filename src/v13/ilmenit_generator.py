"""Generate exact straight-line mountain topology workers, one projected width per ROM bank."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
# Source adapted only to remove import-time output-directory creation.
import re
EXTRA=[int(n) for line in (ROOT/'src/v10_plotter.asm').read_text().split('cull_extra\n',1)[1].split(' ert * >',1)[0].splitlines() if line.strip().startswith('dta ') for n in line.strip()[4:].split(',')]

def source(width,bank,clip=False,dead_x=False,left_clip=False,cull_min=None,cull_precheck=False,layout=None):
    lines=[' opt h-',' org $8000','entry',' stx $60',f' ldy #{width}',f' lda #{EXTRA[width]}',' sta $b5',' lda $84',' cmp $ea',' bcs cull_max',' lda $ea','cull_max',' clc',' adc $b5',' bcc cull_bound',' lda #255','cull_bound',' sta $b5',' ldx $82','cull_scan',' lda $260e,x',' cmp $b5',' bcc render',' inx',' cpx $95',' bcc cull_scan',' ldx $60',' jmp $9900','render',' ldx $82']
    if clip:
        lines[4:4]=[' lda $95',' cmp #212',' bcs render']
    if left_clip:
        assert clip and dead_x
        lines[4:4]=[' lda $82',' cmp #44',' bcc render']
    serial=0;last_x={};cold_chunks=[];cold_helpers={};cull_helpers={}
    max_depth=(width-1).bit_length()-1
    def clip_map(left):
        values={};stopped=False
        def visit(offset,w,depth,right=False):
            nonlocal stopped
            if stopped:return
            if right and left+offset>=212:stopped=True;return
            if w<=2:return
            half=w//2;values[depth+1]=left+offset+half
            visit(offset,half,depth+1)
            visit(offset+half,w-half,depth,True)
        visit(0,width,0)
        return values
    def emit(*args):lines.extend(args)
    def pixel():
        nonlocal serial
        n=serial;serial+=1
        emit(f'pixel_{n}',' cmp $260e,x',f' bcc skip_{n}',f' beq skip_{n}',' sta $260e,x',' cmp #$97',f' bcc address_{n}',' lda #$ff',' sta $260e,x',' lda #$97',f'address_{n}',' tay',' lda row_lo-104,y',' sta $80',' lda row_hi-104,y',' sta $81',' ldy $3900,x',' lda ($80),y',' ora $3800,x',' sta ($80),y',f'skip_{n}')
    def node(offset,w,depth,right=False,parent_width=None):
        nonlocal serial
        if right:
            if clip:
                unique=serial;serial+=1
                emit(' cpx #212',f' bcc continue_{unique}')
                if parent_width==3:emit(' clv')
                if dead_x:emit(f' ldy #{depth}',' ldx $60',' jmp $9900',f'continue_{unique}')
                else:emit(' php',' pha',f' lda #{depth}',' pha',' jmp clipped_return',f'continue_{unique}')
            emit(' stx $82')
        yr=0xea+depth;sr=0xf4+depth
        cull_end=None
        if cull_min is not None and w>=cull_min and (depth>0 or offset>0):
            assert dead_x and not left_clip
            ident=serial;serial+=1;cull_end=f'node_culled_end_{ident}';visible=f'node_visible_{ident}'
            key=(w,depth);helper=cull_helpers.get(key)
            if helper is None:
                helper=f'node_cull_{ident}';cull_helpers[key]=helper
                chunk=[helper,' lda $84',f' cmp ${yr:02x}',f' bcs node_max_{ident}',f' lda ${yr:02x}',f'node_max_{ident}',' clc',f' adc #{EXTRA[w]}',f' bcc node_bound_{ident}',' lda #255',f'node_bound_{ident}',' sta $b5']
                for column in range(w):chunk.extend([f' lda ${0x260e+column:04x},x',' cmp $b5',f' bcs node_scan_{ident}_{column}',' clc',' rts',f'node_scan_{ident}_{column}'])
                chunk.extend([' sec',' rts']);cold_chunks.append(chunk)
            if cull_precheck:emit(' lda $84',' cmp $260e,x',f' bcs {visible}',f' lda ${yr:02x}',' cmp $260e,x',f' bcs {visible}')
            emit(f' jsr {helper}',f' bcc {visible}',f' lda ${yr:02x}',' sta $84',' txa',' clc',f' adc #{w-1}',' tax',f' jmp {cull_end}',visible)
        right_label=None
        if left_clip and offset<44 and w>=2:
            ident=serial;serial+=1;normal=f'left_normal_{ident}';cold=f'left_cold_{ident}';right_label=f'left_right_{ident}';half=w//2;delta=(w-half)//2
            shared=cold_helpers.get((w,depth))
            if shared is None:cold_helpers[w,depth]=cold;shared=cold
            left_split=f'left_split_{ident}' if w>2 else normal
            emit(' cpx #44',f' bcs {normal}',f' jsr {shared}',f' bcc {left_split}',f' jmp {right_label}',normal)
            chunk = None
            if w==2:
                chunk=[cold,' lda #44',' sta $82',' tax',' lda $86',' sec',f' adc ${sr:02x}',' sta $86',f' bpl left_flat_pair_{ident}',' lda #0',' sta $b5',f'left_flat_pair_{ident}',' clv',f' jmp {right_label}']
            if shared==cold:
                if w>2:
                    chunk=[cold,' txa',' clc',f' adc #{half}',' cmp #45',f' bcs compact_above_{ident}',' sta $82',' tax',f' lda #{delta}',' sta $b4',f' jmp compact_seed_{ident}',f'compact_above_{ident}',f' lda #{128+half//2}',' sta $b4',f'compact_seed_{ident}',' lda $86',' sec',f' adc ${sr:02x}',' bit $b4',f' bmi compact_seed_above_{ident}',' sta $86',f' jmp compact_seed_done_{ident}',f'compact_seed_above_{ident}',f' sta ${sr+1:02x}',f'compact_seed_done_{ident}',' ora #0',f' bmi compact_perturb_{ident}',' clc',' lda $84',f' adc ${yr:02x}',' ror @',f' jmp compact_store_{ident}',f'compact_perturb_{ident}',' lda $b4',' and #127',' sta $b5',f' bcs compact_positive_{ident}',' clc',' lda $84',f' adc ${yr:02x}',' ror @',' sec',' sbc $b5',f' bcs compact_neg_ok_{ident}',' lda #0',f'compact_neg_ok_{ident}',f' jmp compact_store_{ident}',f'compact_positive_{ident}',' clc',' lda $84',f' adc ${yr:02x}',' ror @',' clc',' adc $b5',f' bcc compact_pos_ok_{ident}',' lda #$ff',f'compact_pos_ok_{ident}',f'compact_store_{ident}',' bit $b4',f' bmi compact_store_above_{ident}',' sta $84',' sec',' rts',f'compact_store_above_{ident}',f' sta ${yr+1:02x}',' clc',' rts']
                converted=[]
                for instruction in chunk:
                    if instruction==f' jmp {normal}':converted.extend([' clc',' rts'])
                    elif instruction==f' jmp {right_label}':converted.extend([' sec',' rts'])
                    else:converted.append(instruction)
                cold_chunks.append(converted)
        if w==1:
            if left_clip:emit(' clv')
            emit(f' lda ${yr:02x}',' sta $84');pixel();return
        if w==2:
            emit(' sec',f' lda ${yr:02x}',' adc $84',' ror @');pixel()
            emit(' inx')
            if right_label:emit(right_label)
            emit(f' lda ${yr:02x}',' sta $84');pixel();return
        half=w//2;last_x[depth+1]=offset+half;n=serial;serial+=1
        emit(' lda $86',' sec',f' adc ${sr:02x}',f' sta ${sr+1:02x}',f' bmi perturb_{n}',' clc',' lda $84',f' adc ${yr:02x}',' ror @',f' sta ${yr+1:02x}',f' jmp split_{n}',f'perturb_{n}',f' bcs positive_{n}',f' lda #{(half-1)//2}',' sta $b5',' clc',' lda $84',f' adc ${yr:02x}',' ror @',' sbc $b5',f' bcs negative_ok_{n}',' lda #0',f'negative_ok_{n}',f' sta ${yr+1:02x}',f' jmp split_{n}',f'positive_{n}',f' lda #{half//2}',' sta $b5',' clc',' lda $84',f' adc ${yr:02x}',' ror @',' adc $b5',f' bcc positive_ok_{n}',' lda #$ff',f'positive_ok_{n}',f' sta ${yr+1:02x}',f'split_{n}')
        if right_label:emit(left_split)
        node(offset,half,depth+1)
        emit(' inx',f' lda ${sr+1:02x}',' sta $86')
        if right_label:emit(right_label)
        node(offset+half,w-half,depth,True,w)
        if cull_end:emit(cull_end)
    node(0,width,0)
    if not dead_x:
        emit(' php',' pha')
        for depth,offset in sorted(last_x.items()):emit(' txa',' sec',f' sbc #{width-1-offset}',f' sta ${0x95+depth:02x}')
        emit(' pla',' plp')
    emit(' ldy #255',' ldx $60',' jmp $9900')
    if clip and not dead_x:
        emit('clipped_return',' lda $95',' sec',f' sbc #{width}',' tay')
        for depth in range(1,max_depth+1):emit(f' lda clip_x_{depth},y',' cmp #255',f' beq untouched_{depth}',f' sta ${0x95+depth:02x}',f'untouched_{depth}')
        emit(' pla',' tay',' pla',' plp',' ldx $60',' jmp $9900')
    remaining_cold=[]
    def length(block):
        n=0
        for line in block:
            if not line.startswith(' '):continue
            parts=line.strip().split(None,1);op=parts[0];arg=parts[1] if len(parts)>1 else ''
            if op in ('opt','org'):continue
            if op.startswith('b') and op!='bit':n+=2
            elif op in ('jmp','jsr'):n+=3
            elif not arg or arg=='@':n+=1
            elif arg.startswith('#') or arg.startswith('('):n+=2
            elif re.match(r'^\$[0-9a-fA-F]{1,2}(?:,|$)',arg):n+=2
            else:n+=3
        return n
    if layout=='linear':
        return '\n'.join(lines+['hot_end','cold_helpers_begin',f'; cold_helper_bytes={sum(length(c) for c in cold_chunks)}']+[line for chunk in cold_chunks for line in chunk]+['cold_helpers_end'])+'\n'
    assert layout is None,layout
    used=length(lines)
    for chunk in cold_chunks:
        if used+length(chunk)<=0x182f:emit(*chunk);used+=length(chunk)
        else:remaining_cold.append(chunk)
    emit('worker_end',' ert * > $982f',' :($982f-*) dta $ff',' jmp $8000',' :($9834-*) dta $ff',' jmp $8000',' :($9853-*) dta $ff',' jmp $8000',' :($9900-*) dta $ff',' php',' pha',' lda #2',' sta $d500',' ert * <> $9907')
    if remaining_cold:
        emit(' :($990a-*) dta $ff')
        for chunk in remaining_cold:emit(*chunk)
    if clip and not dead_x:
        emit(' :($990a-*) dta $ff')
        for depth in range(1,max_depth+1):emit(f'clip_x_{depth}',' dta '+','.join(str(clip_map(left).get(depth,255)) if 44<=left<212 and left+width<=255 else '255' for left in range(256)))
    emit(f' :(${0x9f68 if clip else 0x9e68:04x}-*) dta $ff','row_lo',' dta '+','.join(str((0x1010+96*(151-y))&255) for y in range(104,152)),f' :(${0x9fa8 if clip else 0x9ea8:04x}-*) dta $ff','row_hi',' dta '+','.join(str((0x1010+96*(151-y))>>8) for y in range(104,152)),' :($9fff-*) dta $ff',f' dta {bank}')
    return '\n'.join(lines)+'\n'
