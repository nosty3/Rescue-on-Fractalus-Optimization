"""Dwa symulatory 6502 w kroku: A = gra z kartridża (XEGS, 64 KB), B = gra po relokacji pod .xex (PORTB).
Start: stan zrzucony z Altirry przy RUN kartridża ($A122, xex/run.img + run.json). Prosty model sprzętu wspólny
dla obu: VCOUNT i RANDOM z licznika cykli, WSYNC = do końca linii, VBI (NMI) co 312 x 114 cykli przy NMIEN bit 6,
wejście (joystick, fire, START) ze skryptu na klatkę. Bez DLI, IRQ i DMA (oba symulatory liczą tak samo).

Po każdej instrukcji: PC_B == M(PC_A), rejestry równe albo zmapowane (starszy bajt adresu, numer banku -> PORTB),
zapisy w pamięci pod odpowiadającymi adresami z równymi albo zmapowanymi wartościami. Zapisy sprzętu (poza
$D500/$D301) muszą być równe. Pierwsza niezgodność = przeoczona albo błędna relokacja; wypisujemy ostatnie kroki.
Użycie (jako moduł): run(rom, ext, steps, inputs) -> raport."""
import collections
from py65.devices.mpu6502 import MPU
from reloc import M, Mhi, portb, USED

LINE = 114
FRAME = 312 * LINE
INV_PORTB = {portb(n): n for n in USED}


class MemA(bytearray):
    def init(self, rom):
        self.rom = rom; self.bank = None; self.log = []; self.romw = []
        bytearray.__setitem__(self, slice(0xA000, 0xC000), rom[15 * 8192:16 * 8192])

    def select(self, b):
        b &= 15
        if b != self.bank:
            self.bank = b
            bytearray.__setitem__(self, slice(0x8000, 0xA000), self.rom[b * 8192:(b + 1) * 8192])

    def __setitem__(self, addr, v):
        self.log.append((addr, v))
        if addr < 0x8000:
            bytearray.__setitem__(self, addr, v)
        elif 0xD500 <= addr < 0xD600:
            self.select(v)
        elif addr < 0xC000:
            self.romw.append(addr)


class MemB(bytearray):
    def init(self, ext):
        self.ext = {n: bytearray(b) for n, b in ext.items()}
        self.cur = None; self.log = []; self.portb = 0xFF
        self.main47 = bytearray(0x4000)

    def setportb(self, v):
        self.portb = v
        # odłóż okno
        if self.cur is not None:
            dst = self.ext[self.cur] if self.cur != "main" else self.main47
            dst[:] = bytearray.__getitem__(self, slice(0x4000, 0x8000))
        n = INV_PORTB.get(v) if not v & 0x10 else "main"
        if n is None:
            n = "main"          # wartość spoza tabeli: porównanie zapisu i tak zgłosi niezgodność
        src = self.ext[n] if n != "main" else self.main47
        bytearray.__setitem__(self, slice(0x4000, 0x8000), src)
        self.cur = n

    def __setitem__(self, addr, v):
        self.log.append((addr, v))
        if addr < 0xC000:
            bytearray.__setitem__(self, addr, v)
        elif addr == 0xD301:
            self.setportb(v)


def hw_before(m, cyc):
    """Rejestry tylko do odczytu, liczone z cykli (identycznie w A i B)."""
    m_set = bytearray.__setitem__
    m_set(m, 0xD40B, (cyc // LINE // 2) % 156)
    m_set(m, 0xD20A, ((cyc * 2654435761) >> 13) & 0xFF)


STROBES = {0xD40A, 0xD40F, 0xD01E, 0xD209, 0xD20A, 0xD20B}   # zapis liczy się, wartość nie (WSYNC, NMIRES...)
MODE_LINES = {2: 8, 3: 10, 4: 8, 5: 16, 6: 8, 7: 16, 8: 8, 9: 4, 10: 4, 11: 2, 12: 1, 13: 2, 14: 1, 15: 1}
DL_FIRST = (312 - 248 + 8) * LINE      # linia 8 obrazu liczona od VBI (linia 248)


def dli_lines(mem, dl):
    """Linie ekranu (8..247) z DLI dla display listy pod adresem dl."""
    out = []; line = 8; pc = dl
    for _ in range(256):
        b = mem[pc & 0xFFFF]; mode = b & 15
        if mode == 0:
            n = ((b >> 4) & 7) + 1; pc += 1
        elif mode == 1:
            if b & 0x80:
                out.append(line)
            if b & 0x40:
                break
            pc = mem[(pc + 1) & 0xFFFF] | mem[(pc + 2) & 0xFFFF] << 8
            line += 1
            continue
        else:
            n = MODE_LINES[mode]; pc += 3 if b & 0x40 else 1
        line += n
        if b & 0x80:
            out.append(line - 1)
        if line >= 248:
            break
    return [x for x in out if x < 248]


class Sim:
    def __init__(self, mem, regs):
        self.mem = mem
        self.cpu = MPU(memory=mem, pc=regs["pc"])
        c = self.cpu
        c.a, c.x, c.y, c.sp, c.p = regs["a"], regs["x"], regs["y"], regs["sp"], regs["p"]
        self.nmien = 0x40
        self.frame = c.processorCycles // FRAME
        self.dl = 0; self.dmactl = 0
        self.lineidx = 0; self.ant_on = False; self.ant_rem = 0; self.ant_dli = 0; self.pending_dli = False
        self.dli_count = 0

    def io_writes(self, log):
        """Obsługa zapisów sprzętu po kroku: NMIEN, NMIRES, WSYNC, DLISTL/H, DMACTL."""
        for addr, v in log:
            if addr == 0xD40E:
                self.nmien = v
            elif addr == 0xD40F:
                bytearray.__setitem__(self.mem, 0xD40F, 0x1F)
            elif addr == 0xD40A:
                c = self.cpu
                c.processorCycles += (-c.processorCycles) % LINE
            elif addr == 0xD402:
                self.dl = self.dl & 0xFF00 | v
            elif addr == 0xD403:
                self.dl = self.dl & 0xFF | v << 8
            elif addr == 0xD400:
                self.dmactl = v

    def scanline(self, i):
        """ANTIC na początku linii i klatki (0 = linia 248, VBI): pobiera instrukcje listy z DLISTL (self.dl),
        na ostatniej linii instrukcji z bitem DLI zgłasza DLI."""
        sl = (i + 248) % 312
        if sl == 8:
            self.ant_on = bool(self.dmactl & 0x20); self.ant_rem = 0
        if not self.ant_on or not 8 <= sl < 248:
            return
        m = self.mem
        if self.ant_rem == 0:
            b = m[self.dl]; mode = b & 15
            if mode == 0:
                n = ((b >> 4) & 7) + 1; self.dl = (self.dl + 1) & 0xFFFF
            elif mode == 1:
                tgt = m[(self.dl + 1) & 0xFFFF] | m[(self.dl + 2) & 0xFFFF] << 8
                self.dl = tgt; n = 1
                if b & 0x40:
                    self.ant_on = False
                    if b & 0x80:
                        self.pending_dli = True
                    return
            else:
                n = MODE_LINES[mode]; self.dl = (self.dl + (3 if b & 0x40 else 1)) & 0xFFFF
            self.ant_rem = n; self.ant_dli = b & 0x80
        self.ant_rem -= 1
        if self.ant_rem == 0 and self.ant_dli:
            self.pending_dli = True

    def tick(self, inputs):
        """Przed krokiem: rejestry z cykli, VBI na początku klatki, ANTIC linia po linii (DLI)."""
        c = self.cpu
        cyc = c.processorCycles
        hw_before(self.mem, cyc)
        f = cyc // FRAME
        if f > self.frame:
            self.frame = f
            self.lineidx = 0; self.ant_on = False
            inp = inputs(f)
            bytearray.__setitem__(self.mem, 0xD300, inp.get("porta", 0xFF))
            bytearray.__setitem__(self.mem, 0xD010, inp.get("trig", 1))
            bytearray.__setitem__(self.mem, 0xD01F, inp.get("consol", 0x07))
            if self.nmien & 0x40:
                bytearray.__setitem__(self.mem, 0xD40F, 0x5F)
                c.nmi()
                return True
        li = (cyc - f * FRAME) // LINE
        while self.lineidx < li:
            self.lineidx += 1
            self.scanline(self.lineidx)
        if self.pending_dli:
            self.pending_dli = False
            if self.nmien & 0x80:
                bytearray.__setitem__(self.mem, 0xD40F, 0x9F)
                self.dli_count += 1
                c.nmi()
                return True
        return False


# Trampoliny tylko w B (adres B -> o ile cykli B jest wolniejszy na całej ścieżce); po wejściu B wykonuje je
# bez odpowiednika w A, a potem wyrównujemy licznik cykli B do A.
TRAMP_B = {0xBF80: 4}      # koniec kodu rezydentnego: jmp $BCA4 przez granicę $8000 -> bne -128 + jmp $7CA4
MARKER_PCS = {0xBFDA, 0xBFDD, 0xBFEA, 0xBFEB, 0xBFED}   # strażnik VBI: znacznik $9FFF od odczytu do skoku (układ A)


def same_val(va, vb, pc=None):
    if va == vb:
        return "eq"
    if pc in MARKER_PCS and ((va == 0xFF and vb == 0) or (va < 16 and vb == portb(va))):
        return "marker"
    if Mhi(va) == vb:
        return "hi"
    if va < 16 and portb(va) == vb:
        return "bank"
    return None


def run(rom, ext, img, regs, steps, inputs, hist=40, report_every=0, stop_at=None, resident=None):
    """resident: zawartość $8000-$BFFF dla B (przeniesiony kod rezydentny); domyślnie surowa kopia $4000-$7FFF A."""
    ma = MemA(img); ma.init(rom); ma.select(regs.get("bank", 0))
    imgb = bytearray(img)
    imgb[0x8000:0xC000] = resident if resident is not None else img[0x4000:0x8000]
    mb = MemB(imgb); mb.init(ext)
    mb.main47[:] = bytes(0x4000)
    mb.setportb(portb(regs.get("bank", 0)))
    A = Sim(ma, regs); B = Sim(mb, dict(regs, pc=M(regs["pc"])))
    trail = collections.deque(maxlen=hist)
    mapped_w = collections.Counter(); mapped_r = collections.Counter()
    last_mapped = {}          # adres -> (PC, bank, krok, wartość A, wartość B) ostatniego zmapowanego zapisu
    run.last_mapped = last_mapped
    ca, cb = A.cpu, B.cpu
    for i in range(steps):
        if ca.processorCycles != cb.processorCycles:
            return dict(ok=False, step=i, why=f"cykle {ca.processorCycles} != {cb.processorCycles}", trail=list(trail))
        A.tick(inputs); B.tick(inputs)
        pa, pb = ca.pc, cb.pc
        bank = ma.bank
        trail.append((pa, pb, bank, ca.a, ca.x, ca.y, cb.a, cb.x, cb.y))
        if pb != M(pa):
            return dict(ok=False, step=i, why=f"PC A ${pa:04x} (bank {bank}) B ${pb:04x}", trail=list(trail))
        if stop_at and pa == stop_at:
            return dict(ok=True, step=i, why="stop_at", mapped_w=mapped_w, mapped_r=mapped_r, frame=A.frame)
        ma.log = []; mb.log = []
        ca.step(); cb.step()
        if cb.pc in TRAMP_B:
            fudge = TRAMP_B[cb.pc]
            while cb.pc in TRAMP_B or cb.pc == M(ca.pc) and False:
                cb.step()
            cb.processorCycles -= fudge
        la, lb = ma.log, mb.log
        A.io_writes(la); B.io_writes(lb)
        if len(la) != len(lb):
            return dict(ok=False, step=i, why=f"liczba zapisów {la} {lb} @ ${pa:04x}", trail=list(trail))
        for (aa, va), (ab, vb) in zip(la, lb):
            if 0xD500 <= aa < 0xD600:
                if ab != 0xD301 or portb(va) != vb:
                    return dict(ok=False, step=i, why=f"bank A ${aa:04x}={va} B ${ab:04x}=${vb:02x} @ ${pa:04x}", trail=list(trail))
                continue
            if ab != M(aa):
                return dict(ok=False, step=i, why=f"zapis A ${aa:04x} B ${ab:04x} @ ${pa:04x} bank {bank}", trail=list(trail))
            if aa in STROBES:
                continue
            k = same_val(va, vb, pa)
            if k is None or (k != "eq" and 0xD000 <= aa < 0xD800):
                return dict(ok=False, step=i, why=f"wartość A ${aa:04x}=${va:02x} B=${vb:02x} @ ${pa:04x} bank {bank}", trail=list(trail))
            if k != "eq":
                mapped_w[(pa, bank, aa, k)] += 1
                last_mapped[aa] = (pa, bank, i, va, vb)
            elif aa in last_mapped:
                del last_mapped[aa]
        for ra, rb, nm in ((ca.a, cb.a, "A"), (ca.x, cb.x, "X"), (ca.y, cb.y, "Y")):
            if ra != rb:
                k = same_val(ra, rb, pa)
                if k is None:
                    return dict(ok=False, step=i, why=f"rejestr {nm} A=${ra:02x} B=${rb:02x} po ${pa:04x} bank {bank}", trail=list(trail))
                mapped_r[(pa, bank, nm, k)] += 1
        if ma.romw:
            return dict(ok=False, step=i, why=f"zapis w ROM ${ma.romw[0]:04x} @ ${pa:04x} bank {bank}", trail=list(trail))
        if report_every and i % report_every == 0 and i:
            print(f"  krok {i} klatka {A.frame} PC ${pa:04x} bank {bank}", flush=True)
    return dict(ok=True, step=steps, why="limit", mapped_w=mapped_w, mapped_r=mapped_r, frame=A.frame, dli=A.dli_count)
