"""Tablice mnożenia dla VBI (łatka vbi2_mul): bank 7 (8 KB, dotąd martwa kopia stałego banku).
Oryginał $7CD6 (kod rezydentny) liczy A = f(M, N) dla M = $6B, N = $28D6 pętlą shift-add z zaokrąglaniem
w górę w każdym kroku: f(M, N) = suma po ustawionych bitach j N z ceil((M >> (7-j)) / 2) mod 256.
Suma jest liniowa w bitach N (mod 256), więc f(M, N) = T1[N >> 4][M] + T2[N & 15][M]:
  T1: strona $80 + (N >> 4), indeks M = f(M, (N >> 4) << 4)
  T2: strona $90 + ((N & 15) ^ 8), indeks M = f(M, N & 15)  (xor 8, żeby $9FFF = f(255, 7) = 7 = znacznik banku)
Funkcja f jest tu emulacją oryginalnej pętli (nie wzorem), a liniowość sprawdzana dla wszystkich 65536 par."""


def f_orig(m, n):
    a = 0
    while True:
        n <<= 1
        c = (n >> 8) & 1
        n &= 0xFF
        if c:
            cm = m & 1
            m >>= 1
            a = (a + m + cm) & 0xFF
            continue
        m >>= 1
        if m == 0:
            return a


def bank7():
    t = bytearray(8192)
    for nh in range(16):
        for m in range(256):
            t[nh * 256 + m] = f_orig(m, nh << 4)
    for nl in range(16):
        page = 16 + (nl ^ 8)
        for m in range(256):
            t[page * 256 + m] = f_orig(m, nl)
    for n in range(256):
        for m in range(256):
            assert (t[(n >> 4) * 256 + m] + t[(16 + ((n & 15) ^ 8)) * 256 + m]) & 0xFF == f_orig(m, n), (m, n)
    assert t[0x1FFF] == 7, t[0x1FFF]
    return bytes(t)


if __name__ == "__main__":
    t = bank7()
    print("ok, $9FFF =", t[0x1FFF], "f(57,96) =", f_orig(57, 96))
