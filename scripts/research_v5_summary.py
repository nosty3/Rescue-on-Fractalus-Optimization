from session import *
from collections import defaultdict,Counter
OUT=ROOT/'results/research_v5';T=106704000
names={'2:982a':'mountain','2:9308':'fill','2:8224':'division','2:87d3':'terrain_other','2:8309':'geometry','2:85d4':'projection_other','2:9627':'clipping','2:9214':'clear','ram:7eeb':'interpolation','ram:7310':'flight_logic','ram:b91c':'sound_main','ram:b46c':'VBI','ram:7cd6':'multiply_RAM','2:814c':'multiply_ROM','ram:aeef':'DLI_WSYNC'}
def location(g):
 n=int(g[1:],16)
 return f'{(n>>16)&255}:{0x8000+(n&8191):04x}' if n>>28==8 else f'ram:{n&65535:04x}'
allrows=[];hot=defaultdict(list)
for scenario in ('straight','right','left','fast_right'):
 tree=json.loads((OUT/f'{scenario}-callgraph.json').read_text());agg=defaultdict(lambda:[0,0,0])
 for r in tree:
  key=location(r['gaddr']);v=agg[key];v[0]+=r['calls'];v[1]+=r['excl_cycles'];v[2]+=r['incl_cycles']
 for k,label in names.items():
  calls,own,inc=agg[k];allrows.append({'scenario':scenario,'key':k,'name':label,'calls':calls,'own':own,'inclusive':inc,'own_percent':own*100/T});hot[k].append([calls,own,inc])
summary={k:{'name':names[k],'mean_calls':sum(x[0] for x in v)/4,'mean_own':sum(x[1] for x in v)/4,'mean_inclusive':sum(x[2] for x in v)/4,'own_percent':sum(x[1] for x in v)/4*100/T,'own_percent_range':[min(x[1] for x in v)*100/T,max(x[1] for x in v)*100/T]} for k,v in hot.items()}
trace=json.loads((OUT/'renderer-trace.json').read_text());div=trace['division_inputs'];sh=Counter(x['shift'] for x in div)
stats={'divider_calls':len(div),'normalization_shifts':dict(sh),'mean_shifts':sum(x['shift'] for x in div)/len(div),'same_previous_divisor':sum(x['same_previous_divisor'] for x in div),'unique_divisors':len({x['d'] for x in div}),'zero_numerators':sum(x['n']==0 for x in div),'total_pixel_writes':trace['pixel']['writes'],'consecutive_pixel_same_address':trace['pixel']['consecutive_same_address'],'fill_first_above32':sum(v for k,v in trace['fill_first_rows'].items() if int(k)>32),'fill_columns':sum(trace['fill_first_rows'].values()),'total_page_penalties':sum(trace['page_penalties'].values()),'branch_page_penalties':0}
rom=(ROOT/'dist/Rescue on Fractalus! - PAL optimized v5 128KB.rom').read_bytes();stats['empty_rom_banks']=[b for b in range(16) if rom[b*8192:(b+1)*8192]==b'\xff'*8192]
branches={0x10,0x30,0x50,0x70,0x90,0xb0,0xd0,0xf0}
for key,n in trace['page_penalties'].items():
 bank,pc=key.split(':');pc=int(pc,16);bank=int(bank)
 if 0x8000<=pc<0xa000 and rom[bank*8192+pc-0x8000] in branches:stats['branch_page_penalties']+=n
out={'ticks_each':T,'profiles':allrows,'summary':summary,'trace_statistics':stats}
(OUT/'summary.json').write_text(json.dumps(out,indent=2))
for k,v in summary.items():print(k,v)
print(stats)
