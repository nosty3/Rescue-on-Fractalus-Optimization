import sys, pathlib, json
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.dont_write_bytecode=True
packages=list((ROOT/'tools/bridge').glob('*'))
if packages:sys.path.insert(0,str(packages[0]/'sdk/python'))
def connect():
    packages=list((ROOT/'tools/bridge').glob('*'))
    if not packages: raise RuntimeError('Install Altirra bridge under tools/bridge first; see docs/ODTWORZENIE_PL.md')
    sys.path.insert(0,str(packages[0]/'sdk/python'))
    from altirra_bridge import AltirraBridge
    return AltirraBridge.from_token_file(str(next((ROOT/'tools').glob('*.token'))))
