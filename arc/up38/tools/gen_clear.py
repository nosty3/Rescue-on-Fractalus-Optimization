"""Generuje src/clear_b6.asm (bufor X=3) i src/clear_b8.asm (X=51): kasowanie bufora w kolejności wierszy
od góry z wyścigiem z promieniem. Zastępuje banki 6/8 nosty3 (clear128_bank6/8), te same punkty stałe:
wejście $9863 (plp / jmp $8000), powrót $98F0 (php / pha / lda #2 / sta $d500 -> bank 2 $98F7 pla/plp/rts).

Zbiór zapisanych bajtów i wartość (0) identyczne jak w oryginale $9214: wiersze 0..43 kolumn X..X+41
plus brzegi wierszy 44-47. Kolejność: wiersz po wierszu. Przed parą wierszy r, r+1 (r >= 1):
jeśli VBI ($4A <> 0) jeszcze nie przełączył obrazu ($42 <> 0), czekamy aż VCOUNT >= 26 + r + 1, czyli aż
ANTIC pobrał już oba wiersze w tej ramce (wiersz r bufora: linia 48 + 2r). Na końcu pełne czekanie jak
wait_beam (VCOUNT 74..123 albo $42 = 0), bo dalej rysowanie gór pisze w dowolne wiersze.
Rejestry na wyjściu jak u nosty3: A = 0, Y = 0, X = $94 (= X wejścia)."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BOTTOM = ([0x2090 + k for k in range(5)] + [0x20BA - k for k in range(6)] + [0x20F0 + k for k in range(4)] +
          [0x211A - k for k in range(5)] + [0x2150 + k for k in range(3)] + [0x217A - k for k in range(4)] +
          [0x21B0, 0x21DA, 0x21B1, 0x21D9, 0x21D8])  # oryginał $92A7-$9304, + X


def gen(x0, bank):
    L = [f"; Kasowanie bufora X={x0} (bank {bank}), wiersze od góry, wyścig z promieniem. Generuje gen_clear.py.",
         " opt h-", " org $8000",
         " stx $94", " lda #0"]

    def beam(k, lab):
        return [f"{lab}", " ldy $4a", f" beq {lab}_ok", " ldy $42", f" beq {lab}_ok",
                " ldy $d40b", f" cpy #{k}", f" bcc {lab}", f"{lab}_ok"]

    for r in range(44):
        if r >= 1 and r % 2 == 1:
            L += beam(26 + min(r + 1, 43), f"b{r}")
        base = 0x1010 + 96 * r + x0
        L += [f" sta ${base + c:04x}" for c in range(42)]
    L += beam(74, "b44")
    L += [f" sta ${a + x0:04x}" for a in BOTTOM]
    # pełne czekanie przed rysowaniem (jak wait_beam)
    L += ["wfin", " ldy $4a", " beq wfin_ok", " ldy $42", " beq wfin_ok",
          " ldy $d40b", " cpy #74", " bcc wfin", " cpy #124", " bcs wfin", "wfin_ok",
          " ldy #0", " ldx $94", " jmp $98f0",
          " ert * > $9863", " :($9863-*) dta $ff",
          " plp", " jmp $8000",
          " :($98f0-*) dta $ff",
          " php", " pha", " lda #2", " sta $d500",
          " ert * <> $98f7",
          " :($9fff-*) dta $ff", f" dta {bank}"]
    open(f"{ROOT}/src/clear_b{bank}.asm", "w").write("\n".join(L) + "\n")


assert len(BOTTOM) == 32
gen(3, 6)
gen(51, 8)
print("zapisano src/clear_b6.asm, src/clear_b8.asm")
