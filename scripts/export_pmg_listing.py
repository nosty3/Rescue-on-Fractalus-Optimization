from opt14_cpu import *
from py65.disassembler import Disassembler
out=ROOT/'results/pmg_audit'; rom=(ROOT/'build/buffer_sync.rom').read_bytes(); old=(ROOT/'Rescue on Fractalus!.rom').read_bytes()
c=machine(rom,(ROOT/'analysis/flying-ram.bin').read_bytes()); dis=Disassembler(c)
ranges=[(0xa000,0xa03d,'Inicjalizacja, w tym zerowanie PMG'),(0xa0a1,0xa0bf,'Uniwersalne wypelnianie pamieci'),(0xa527,0xa5a8,'Wskaznik 21 wierszy, pasek i pocisk'),(0xa632,0xa69c,'Aktualizacja paska w P1'),(0xa71e,0xa83e,'Kasowanie i rysowanie obiektu P3'),(0xa8de,0xa93e,'Obiekt P3 o wysokosci 5 wierszy'),(0xa94d,0xa994,'Znacznik M2 o wysokosci 3 wierszy'),(0xaa65,0xaa7d,'Inicjalizacja 3 x 8 bajtow'),(0x710d,0x726a,'Renderer P2 w RAM: kasowanie, wybor ksztaltu, powtarzanie wierszy'),(0x4fc2,0x5014,'Przewijanie czterech graczy i nowy wiersz')]
lines=['; Audyt PMG v8. Wybrane procedury od znanych punktow wejscia.', '; RAM pochodzi z historycznego stanu lotu; kod PMG nie byl zmieniany.']
for start,end,label in ranges:
    if start>=0xa000: assert rom[-8192+start-0xa000:-8192+end-0xa000]==old[-8192+start-0xa000:-8192+end-0xa000]
    lines.append('\n; '+label); pc=start
    while pc<end:
        n,s=dis.instruction_at(pc); lines.append(f'{pc:04X}  '+bytes(c.memory[pc:pc+n]).hex(' ').ljust(9)+' '+s); pc+=n
(out/'PROCEDURY_PMG_PL.txt').write_text('\n'.join(lines),encoding='utf-8')
print('Exported known-entry listing; ROM routines equal original')
