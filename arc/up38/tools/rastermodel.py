"""Model w Pythonie oryginalnej rasteryzacji $982A-$9A54 (bank 2 oryginału), bit w bit.
Stan: L = ($82 x, $84 h, $86 faza), stos prawych końców y: sx=$95+y, sh=$EA+y, sp=$F4+y; occ = $260E+x.
raster() modyfikuje occ i zwraca listę pikseli (kolumna, wysokość po obcięciu do $97).
stats (opcjonalny dict) zbiera liczniki, a hook(event, ...) pozwala badać poddrzewa."""


def _avg(a, b, c_in):
    s = a + b + c_in
    return s >> 1, s & 1          # wynik ror i C po ror (bit 0 sumy)


def raster(L, R, occ, stats=None, cull=None):
    """cull(x_lo, x_hi, h_l, h_r, w) -> True = poddrzewo na pewno niewidoczne (pomiń). Domyślnie brak."""
    plots = []
    x82, h84, ph86 = L
    sx = [0] * 64; sh = [0] * 64; sp = [0] * 64
    sx[0], sh[0], sp[0] = R
    y = 0

    def plot(col, h):
        if stats is not None:
            stats["tests"] = stats.get("tests", 0) + 1
        if h > occ[col]:
            occ[col] = h
            if h >= 0x97:
                occ[col] = 0xFF; h = 0x97
            plots.append((col, h))

    # $982A
    if sx[0] < 0x2D or sx[0] < x82:
        return plots
    if sx[0] == x82:
        plot(sx[0], sh[0])
        return plots
    # $986D: przycinanie lewej strony
    while x82 < 0x2C:
        mid = (x82 + sx[y]) >> 1                       # clc; adc; ror (bez przeniesienia z dodawania: max 255+255)
        mid = (x82 + sx[y]) >> 1
        t = ph86 + sp[y] + 1; c = t > 0xFF; t &= 0xFF  # sec; adc
        if mid <= 0x2C:                                # $9884: środek -> lewy koniec
            x82 = mid; ph86 = t
            avg = (h84 + sh[y]) >> 1
            if t < 0x80:
                h84 = avg
            else:
                off = ((sx[y] - x82) & 0xFF) >> 1
                h84 = max(0, avg - off) if not c else min(255, avg + off)
        else:                                          # $98D6: środek na stos
            sx[y + 1] = mid; sp[y + 1] = t
            avg = (h84 + sh[y]) >> 1
            if t < 0x80:
                sh[y + 1] = avg
            else:
                off = ((mid - x82) & 0xFF) >> 1
                sh[y + 1] = max(0, avg - off) if not c else min(255, avg + off)
            y += 1
    X = x82
    # $9933
    while True:
        if X >= 0xD4:
            return plots
        x82 = X
        diff = (X - sx[y]) & 0xFF
        if diff == 0xFE:                               # szerokość 2
            hm, _ = _avg(sh[y], h84, 1)
            plot(X, hm)
            X += 1
            h84 = sh[y]
            plot(X, h84)
            y -= 1
            if y < 0:
                return plots
            X += 1
            ph86 = sp[y + 1]
            continue
        if diff == 0xFF:                               # szerokość 1
            h84 = sh[y]
            plot(X, h84)
            y -= 1
            if y < 0:
                return plots
            X += 1
            ph86 = sp[y + 1]
            continue
        # szerokość >= 3 ($99FA, C=0)
        w = (sx[y] - X) & 0xFF
        if cull is not None and cull(X, sx[y], h84, sh[y], w, stats):
            # pominięcie poddrzewa = stan jak po jego przerobieniu: L := R, zdjęcie ze stosu
            h84 = sh[y]
            y -= 1
            if y < 0:
                return plots
            X = sx[y + 1]
            ph86 = sp[y + 1]
            continue
        mid = (X + sx[y]) >> 1
        t = ph86 + sp[y] + 1; c = t > 0xFF; t &= 0xFF
        sx[y + 1] = mid; sp[y + 1] = t
        if t < 0x80:
            hm = (h84 + sh[y]) >> 1
        elif not c:
            off = ((mid - x82 - 1) & 0xFF) >> 1       # sbc $82 z C=0
            avg, cb = _avg(h84, sh[y], 0)
            hm = avg - off - (1 - cb)                  # sbc $b5 z C = bit 0 sumy
            if hm < 0:
                hm = 0
        else:
            off = ((mid - x82) & 0xFF) >> 1           # sbc $82 z C=1
            avg, cb = _avg(h84, sh[y], 0)
            hm = avg + off + cb                        # adc $b5 z C = bit 0 sumy
            if hm > 255:
                hm = 255
        sh[y + 1] = hm
        y += 1
        if stats is not None:
            stats["splits"] = stats.get("splits", 0) + 1
