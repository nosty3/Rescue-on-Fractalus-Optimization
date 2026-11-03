"""Generator of the scene grid code (banks 10-13): `jsr $8309` -> bank 2 dispatch ($9863, quadrant of the heading
in $80) -> bank 10..13 `$9893 jmp $8000` -> 45 terrain points along a spiral -> exit `$98E0` back to bank 2.

The original code (nosty3 base, unchanged since the 1985 game) is a straight-line unrolled spiral. Per point k:
position P_k = P_{k-1} + step (16-bit x at $22a4+k/$22d2+k, z at $2300+k/$232e+k; step = +-A, +-B or, at the
spiral corners, two of them; A = $a0/$a1, B = $a2/$a3), grid index X_k = ((X_{k-1} + dx) & $0f) | b6 with b6 =
row*16 ($b6 += +-$10), heightmap h = $0900[X_k], t = h - $8c - !C0 (C0 = ($8b == 0)), two lookups in the bank
tables $9D00/$9E00 and a view classification of (x, z) into $24b4+k.

This generator parses the original code of each bank (asserting the exact template of every point) and emits
the same computation with identical RAM results and identical A/X/Y/P at the exit:
- grid index by page tables (MV_*: X -> next index for a column or row move) instead of TXA/AND/ORA/TAX,
  the b6 updates in RAM and the LDX reload; $b6 is written once at the end (= X_44 & $f0; X_k & $f0 = b6_k);
- the carry C0 for `sbc $8c` from `cmp K3` (A = previous class value in {0,$20,$40,$80}; K3 = C0 ? 0 : $ff)
  instead of `sec / lda #0 / sbc $8b`;
- t in Y (no reload of X), $9f holds ((-$8b)>>3)>>1 during the routine (restored from the stack as before),
  `sta $b5` only where its last value is decided (point 44), Y instead of $b5 in the negative-x compare;
- the z update last, so the classification starts with the flags of the z high byte (no reload);
- spiral corners: one add of U = A+B or V = A-B (16-bit, mod 2^16 identical to the two adds).
Points 0 and 44 keep the original carry source (`sec / lda #0 / sbc $8b`) so the V flag at the exit is the same.
Scratch: K3 in $80 (restored), U/V in output bytes of point 44 (overwritten later): RAM identical byte for byte."""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

PROLOG = bytes.fromhex("a59f4838a900e58b4a4a4a859fa000")
EPILOG = bytes.fromhex("a868859f98a02dc02d4ce098")
EXIT_STUB = bytes.fromhex("0848a9028d00d5")          # $98E0: php / pha / lda #2 / sta $d500 -> bank 2 $98E7

# scratch (zero page), set by patches_scene.py after the liveness check
# K3 in $80: the bank-2 dispatch left the quadrant code there ($55/$82/$AF/$DC for banks 10..13), restored at the
# end. U and V in bytes of point 44 that are written only after the last spiral corner (idx/hm/t1/t2 of point 44).
# So the RAM after the routine is identical byte for byte, no extra scratch.
ZK3 = 0x80
ZU, ZV = (0x22A2, 0x23E1), (0x23B4, 0x2387)
QUADRANT = {10: 0x55, 11: 0x82, 12: 0xAF, 13: 0xDC}


def w(a):
    return a.to_bytes(2, "little")


def pt_template(k):
    idx = 0x2276 + k
    return (bytes.fromhex("38a900e58b8a290f05b6aa8e") + w(idx) + bytes.fromhex("bd0009")
            + b"\x8d" + w(0x23b5 + k) + bytes.fromhex("e58caab007bd009d09f0d003bd009d")
            + b"\x8d" + w(0x2388 + k) + bytes.fromhex("a59f4a1d009e85b5")
            + b"\x8d" + w(0x235b + k) + b"\xae" + w(idx))


def cls_inline(k):
    zl, zh, xl, xh = 0x2300 + k, 0x232e + k, 0x22a4 + k, 0x22d2 + k
    return (b"\xad" + w(zh) + bytes.fromhex("3044d007") + b"\xad" + w(zl) + bytes.fromhex("c920903b")
            + b"\xad" + w(xh) + bytes.fromhex("101f38a900ed") + w(xl) + bytes.fromhex("85b5a900ed") + w(xh)
            + b"\xcd" + w(zh) + bytes.fromhex("9020d007a5b5cd") + w(zl) + bytes.fromhex("9017a940d019cd") + w(zh)
            + bytes.fromhex("900ed008ad") + w(xl) + b"\xcd" + w(zl) + bytes.fromhex("9004a920d006a900f002a980")
            + b"\x8d" + w(0x24b4 + k))


CLS_SUB = bytes.fromhex("b92e233044d007b90023c920903bb9d222101f38a900f9a42285b5a900f9d222d92e239020d007a5b5d90023"
                        "9017a940d019d92e23900ed008b9a422d900239004a920d006a900f002a98099b42460")


def parse(bank):
    """bank: 8 KB of the original variant bank. Returns the list of events (see module doc)."""
    d = bank
    g = lambda a, n=1: d[a - 0x8000:a - 0x8000 + n]
    assert g(0x8000, len(PROLOG)) == PROLOG
    a = 0x8000 + len(PROLOG)
    ev = []; sub = None; k = 0
    while True:
        o = d[a - 0x8000]; o1 = d[a - 0x7fff]
        if o == 0xA5 and o1 == 0xB6:
            s = g(a, 7)
            assert s[:4] == bytes.fromhex("a5b61869") and s[5:] == bytes.fromhex("85b6") and s[4] in (0x10, 0xF0)
            ev.append(("b6", 1 if s[4] == 0x10 else -1)); a += 7; continue
        if o in (0x18, 0x38) and o1 == 0xAD:
            s = g(a, 17); add = o == 0x18; op = 0x65 if add else 0xE5
            assert s[1] == 0xAD and s[4] == op and s[6] == 0x8D and s[9] == 0xAD and s[12] == op and s[14] == 0x8D
            src, vec, dst = s[2] | s[3] << 8, s[5], s[7] | s[8] << 8
            assert (s[10] | s[11] << 8) == src + 0x2E and s[13] == vec + 1 and (s[15] | s[16] << 8) == dst + 0x2E
            assert vec in (0xA0, 0xA2)
            if 0x22A3 <= dst <= 0x22A3 + 45:
                coord, base = "x", 0x22A4
            else:
                assert 0x22FF <= dst <= 0x22FF + 45, hex(dst)
                coord, base = "z", 0x2300
            ev.append(("pos", coord, dst - base, src - base, 1 if add else -1, "A" if vec == 0xA0 else "B"))
            a += 17; continue
        if o in (0xE8, 0xCA):
            ev.append(("dx", 1 if o == 0xE8 else -1)); a += 1; continue
        if o == 0x38 and o1 == 0xA9:
            t = pt_template(k)
            assert g(a, len(t)) == t, (hex(a), k)
            ev.append(("pt", k)); a += len(t)
            if d[a - 0x8000] == 0xA0:
                assert g(a, 2) == bytes([0xA0, k]) and d[a - 0x7ffe] == 0x20
                s = d[a - 0x7ffd] | d[a - 0x7ffc] << 8
                sub = sub or s
                assert s == sub
                a += 5
            else:
                c = cls_inline(k)
                assert g(a, len(c)) == c, (hex(a), k)
                a += len(c)
            k += 1; continue
        if o == 0x4C:
            assert g(a, 3) == bytes.fromhex("4c0099"); a = 0x9900; continue
        assert g(a, len(EPILOG)) == EPILOG, hex(a)
        break
    assert k == 45 and g(sub, len(CLS_SUB)) == CLS_SUB
    assert g(0x9893, 3) == bytes.fromhex("4c0080") and g(0x98E0, len(EXIT_STUB)) == EXIT_STUB
    return ev


def steps(ev):
    """Per point k: (dx, dy, {coord: (srcs, ca, cb)}) of the events since the previous point."""
    out = []; cur = None
    def new():
        return dict(dx=0, dy=0, pos={"x": [], "z": []})
    cur = new()
    for e in ev:
        if e[0] == "b6":
            cur["dy"] += e[1]
        elif e[0] == "dx":
            cur["dx"] += e[1]
        elif e[0] == "pos":
            cur["pos"][e[1]].append(e[2:])
        elif e[0] == "pt":
            k = e[1]
            for coord, ops in cur["pos"].items():
                ca = cb = 0
                for i, (dst, src, sign, vec) in enumerate(ops):
                    assert dst == k and src == (k - 1 if i == 0 else k), (k, coord, ops)
                    if vec == "A":
                        ca += sign
                    else:
                        cb += sign
                cur["pos"][coord] = (ca, cb) if ops else None
            out.append(cur); cur = new()
    return out


class Asm:
    def __init__(self):
        self.lines = []; self.n = 0

    def __call__(self, s):
        self.lines.append(s)

    def lab(self, name):
        self.lines.append(name)


def pos_code(A, coord, k, ca, cb):
    base_l, base_h = (0x22A4, 0x22D2) if coord == "x" else (0x2300, 0x232E)
    src_l, src_h = base_l + k - 1, base_h + k - 1
    if (ca, cb) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        add = (ca + cb) > 0
        v = (0xA0, 0xA1) if ca else (0xA2, 0xA3)
    else:
        assert k < 44, "U/V live in point-44 bytes"
        assert abs(ca) == 1 and abs(cb) == 1
        if ca == cb:
            add, v = ca > 0, ZU          # +-(A+B)
        else:
            add, v = ca > 0, ZV          # +-(A-B)
    op = "adc" if add else "sbc"
    A(" clc" if add else " sec")
    A(f" lda ${src_l:04x}"); A(f" {op} ${v[0]:02x}"); A(f" sta ${base_l + k:04x}")
    A(f" lda ${src_h:04x}"); A(f" {op} ${v[1]:02x}"); A(f" sta ${base_h + k:04x}")


def mv_name(dx, dy):
    # row moves read one 288-byte ramp R[j] = (j - 16) & $ff: mv_rm = R (page aligned), mv_rp = R + 32
    return {(1, 0): "mv_cp", (-1, 0): "mv_cm", (0, 1): "mv_rm+32", (0, -1): "mv_rm"}[(dx, dy)]


def move_code(A, dx, dy, used):
    parts = []
    if dx:
        parts.append((dx, 0))
    if dy:
        parts.append((0, dy))
    assert parts and all(abs(p[0]) <= 1 and abs(p[1]) <= 1 for p in parts)
    for p in parts:
        used.add(p)
        A(f" lda {mv_name(*p)},x"); A(" tax")


def grid_tail(A, k, last=False):
    """after X = X_k and C = C0: store index, heightmap, t, the two lookups."""
    A(f" stx ${0x2276 + k:04x}")
    if last:
        A(" txa"); A(" and #$f0"); A(" sta $b6")
    A(" lda $0900,x"); A(f" sta ${0x23b5 + k:04x}")
    A(" sbc $8c"); A(" tay")
    A(f" bcs g{k}_c")
    A(" lda $9d00,y"); A(" ora #$f0"); A(f" bne g{k}_s")
    A.lab(f"g{k}_c"); A(" lda $9d00,y")
    A.lab(f"g{k}_s"); A(f" sta ${0x2388 + k:04x}")
    A(" lda $9f"); A(" ora $9e00,y")
    if last:
        A(" sta $b5")
    A(f" sta ${0x235b + k:04x}")


# points whose x < 0 path is inlined (space allows ~30): those with x < 0 in >= 15% of headings (sweep over all
# headings of each quadrant variant on captured states, the same for the four variants); the others call `negx`
NEG_INLINE = set(range(3, 12)) | set(range(20, 39))


def cls_code(A, k, have_zh, last=False):
    zl, zh, xl, xh = 0x2300 + k, 0x232E + k, 0x22A4 + k, 0x22D2 + k
    L = f"c{k}_"
    if not have_zh:
        A(f" lda ${zh:04x}")
    A(f" bmi {L}80"); A(f" bne {L}x")
    A(f" lda ${zl:04x}"); A(" cmp #$20"); A(f" bcc {L}80")
    A.lab(f"{L}x"); A(f" lda ${xh:04x}"); A(f" bpl {L}p")
    if last or k in NEG_INLINE:
        # x < 0: -x (16-bit) >= z -> $40; the low byte of -x in $b5 (last point: its final value) or Y
        A(" sec"); A(" lda #0"); A(f" sbc ${xl:04x}"); A(" sta $b5" if last else " tay")
        A(" lda #0"); A(f" sbc ${xh:04x}"); A(f" cmp ${zh:04x}"); A(f" bcc {L}00"); A(f" bne {L}40")
        A(" lda $b5" if last else " tya"); A(f" cmp ${zl:04x}"); A(f" bcc {L}00")
        A.lab(f"{L}40"); A(" lda #$40"); A(f" bne {L}s")
    else:
        # x < 0 (rare): shared routine indexed by Y = k, stores the class and returns it in A
        A(f" ldy #{k}"); A(" jsr negx"); A(f" jmp pk{k + 2}")   # chunk 0 = prolog, point k = chunk k+1
    A.lab(f"{L}p"); A(f" cmp ${zh:04x}"); A(f" bcc {L}00"); A(f" bne {L}20")
    A(f" lda ${xl:04x}"); A(f" cmp ${zl:04x}"); A(f" bcc {L}00")
    A.lab(f"{L}20"); A(" lda #$20"); A(f" bne {L}s")
    A.lab(f"{L}00"); A(" lda #0"); A(f" beq {L}s")
    A.lab(f"{L}80"); A(" lda #$80")
    A.lab(f"{L}s"); A(f" sta ${0x24B4 + k:04x}")


def gen_points(ev, bank_no):
    """Code of the routine body as a list of chunks (one per point) of asm lines; and the set of moves used."""
    st = steps(ev)
    used = set()
    chunks = []
    # prolog: $9f saved; C0, K3, h = ((-$8b)>>3)>>1 in $9f; U = A+B, V = A-B
    A = Asm()
    # shared x < 0 classification of point Y (same instructions as the original, operands indexed by Y)
    A.lab("negx")
    A(" sec"); A(" lda #0"); A(" sbc $22a4,y"); A(" sta $b5")
    A(" lda #0"); A(" sbc $22d2,y"); A(" cmp $232e,y"); A(" bcc negx_00"); A(" bne negx_40")
    A(" lda $b5"); A(" cmp $2300,y"); A(" bcc negx_00")
    A.lab("negx_40"); A(" lda #$40"); A(" sta $24b4,y"); A(" rts")
    A.lab("negx_00"); A(" lda #0"); A(" sta $24b4,y"); A(" rts")
    A.lab("entry")
    A(" lda $9f"); A(" pha")
    A(" sec"); A(" lda #0"); A(" sbc $8b"); A(" tay")
    A(" lda #0"); A(" sbc #0"); A(f" sta ${ZK3:02x}")         # C0 ? 0 : $ff
    A(" tya"); A(" lsr"); A(" lsr"); A(" lsr"); A(" lsr"); A(" sta $9f")
    A(" clc"); A(" lda $a0"); A(" adc $a2"); A(f" sta ${ZU[0]:04x}"); A(" lda $a1"); A(" adc $a3"); A(f" sta ${ZU[1]:04x}")
    A(" sec"); A(" lda $a0"); A(" sbc $a2"); A(f" sta ${ZV[0]:04x}"); A(" lda $a1"); A(" sbc $a3"); A(f" sta ${ZV[1]:04x}")
    chunks.append(A.lines)
    for k, s in enumerate(st):
        A = Asm()
        if k == 0:
            # b6/dx in the original form (b6 in RAM is read by the point-0 index), then grid, pos, class
            for _ in range(abs(s["dy"])):
                A(" lda $b6"); A(" clc"); A(f" adc #${0x10 if s['dy'] > 0 else 0xF0:02x}"); A(" sta $b6")
            for _ in range(abs(s["dx"])):
                A(" inx" if s["dx"] > 0 else " dex")
            A(" sec"); A(" lda #0"); A(" sbc $8b")
            A(" txa"); A(" and #$0f"); A(" ora $b6"); A(" tax")
            grid_tail(A, k)
            have = False
            for coord in ("x", "z"):
                if s["pos"][coord]:
                    pos_code(A, coord, k, *s["pos"][coord]); have = coord == "z"
            cls_code(A, k, have)
        elif k < 44:
            A(f" cmp ${ZK3:02x}")
            move_code(A, s["dx"], s["dy"], used)
            grid_tail(A, k)
            assert s["pos"]["x"] and s["pos"]["z"]
            pos_code(A, "x", k, *s["pos"]["x"]); pos_code(A, "z", k, *s["pos"]["z"])
            cls_code(A, k, True)
        else:
            assert s["pos"]["x"] and s["pos"]["z"]
            pos_code(A, "x", k, *s["pos"]["x"]); pos_code(A, "z", k, *s["pos"]["z"])
            A(" sec"); A(" lda #0"); A(" sbc $8b")
            move_code(A, s["dx"], s["dy"], used)
            grid_tail(A, k, last=True)
            cls_code(A, k, False, last=True)
            A(" tay"); A(" pla"); A(" sta $9f")
            A(f" lda #${QUADRANT[bank_no]:02x}"); A(f" sta ${ZK3:02x}")     # K3 scratch back to the dispatch value
            A(" tya"); A(" ldy #$2d"); A(" cpy #$2d"); A(" jmp $98e0")
        chunks.append(A.lines)
    return chunks, used


def mv_table(dx, dy):
    return bytes(((((i + dx) & 0x0F) | ((i & 0xF0) + 16 * dy)) & 0xFF) if dx else ((i + 16 * dy) & 0xFF)
                 for i in range(256))


REGIONS = ((None, 0x9893), (0x98E7, 0x9D00), (0x9F00, 0x9FFF))   # code space around the stubs and tables


def gen_source(bank_no, orig, sizes=None):
    """Full 8 KB bank source (MADS). orig: the original 8 KB of the bank. sizes: byte size of every chunk (from
    the first pass); None = first pass (tables + contiguous code only, for the label table). With sizes, the
    chunks are placed into REGIONS in order, with `jmp` to the next region where the next chunk does not fit
    (3 bytes for the jmp are always kept free); the stubs at $9893 (landing from bank 2: jmp entry) and $98E0
    (exit to bank 2), the original tables $9D00-$9EFF and the marker $9FFF are kept."""
    ev = parse(orig)
    chunks, used = gen_points(ev, bank_no)
    assert used == {(1, 0), (-1, 0), (0, 1), (0, -1)}
    L = [f"; generated by tools/gen_scene.py from the v11 bank {bank_no} (scene grid variant), do not edit",
         " opt h-", " org $8000"]
    for p in ((1, 0), (-1, 0)):
        L.append(mv_name(*p))
        t = mv_table(*p)
        for i in range(0, 256, 16):
            L.append(" dta " + ",".join(f"${b:02x}" for b in t[i:i + 16]))
    L.append("mv_rm")
    ramp = bytes((j - 16) & 0xFF for j in range(288))
    assert ramp[:256] == mv_table(0, -1) and ramp[32:288] == mv_table(0, 1)
    for i in range(0, 288, 16):
        L.append(" dta " + ",".join(f"${b:02x}" for b in ramp[i:i + 16]))
    code_start = 0x8000 + 512 + 288
    if sizes is None:
        for i, ch in enumerate(chunks):
            L.append(f"pk{i}"); L.extend(ch)
        L.append("code_end")
        return "\n".join(L) + "\n", len(chunks)
    tab = orig[0x1D00:0x1F00]
    tail = {0: [" :($9893-*) dta $ff", " jmp entry", " :($98e0-*) dta $ff",
                " dta " + ",".join(f"${b:02x}" for b in EXIT_STUB)],
            1: [" :($9d00-*) dta $ff"] + [" dta " + ",".join(f"${b:02x}" for b in tab[i:i + 16])
                                           for i in range(0, 512, 16)],
            2: [" :($9fff-*) dta $ff", f" dta {bank_no}"]}
    r = 0; addr = code_start
    for i, (ch, n) in enumerate(zip(chunks, sizes)):
        if addr + n + 3 > REGIONS[r][1]:
            L.append(f" jmp cont{r}"); L.append(f" ert *>${REGIONS[r][1]:04x}"); L.extend(tail[r])
            r += 1; addr = REGIONS[r][0]
            L.append(f"cont{r - 1}")
            assert addr + n + 3 <= REGIONS[r][1], "scene code does not fit"
        L.append(f"pk{i}"); L.extend(ch); addr += n
    L.append("code_end"); L.append(f" ert *>${REGIONS[r][1]:04x}")
    while r < 3:
        L.extend(tail[r]); r += 1
    return "\n".join(L) + "\n", len(chunks)
