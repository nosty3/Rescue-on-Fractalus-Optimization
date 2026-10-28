"""Ścieżki zewnętrzne narzędzi (jedno miejsce). Każdą można zmienić zmienną środowiskową.
  FRACTALUS_WORK   katalog roboczy (buildy, sceny, wyniki pomiarów)        domyślnie <repo>/work
  FRACTALUS_NOSTY  klon github.com/nosty3/Rescue-on-Fractalus-Optimization domyślnie <WORK>/repo
  FRACTALUS_MADS   mads.exe (Mad-Assembler)                                domyślnie <WORK>/mads/mads.exe
  ALTIRRA_BRIDGE   katalog AltirraBridge (serwer + sdk/python), fork github.com/ilmenit/AltirraSDL
  ALTIRRA_BRIDGE_EXE  serwer z podniesionymi limitami PROFILE_DUMP/HISTORY (covmap.py), domyślnie zwykły serwer"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_local = os.path.join(ROOT, "work")
WORK = os.environ.get("FRACTALUS_WORK", "G:/tmp/claude/atari/fractalus" if os.path.isdir("G:/tmp/claude/atari/fractalus")
                      else _local).replace("\\", "/")
NOSTY = os.environ.get("FRACTALUS_NOSTY", f"{WORK}/repo").replace("\\", "/")
MADS = os.environ.get("FRACTALUS_MADS", f"{WORK}/mads/mads.exe").replace("\\", "/")
_home_bridge = os.path.expanduser("~/.claude/tools/altirra-bridge")
BRIDGE = os.environ.get("ALTIRRA_BRIDGE", _home_bridge if os.path.isdir(_home_bridge)
                        else os.path.join(ROOT, "altirra-bridge")).replace("\\", "/")
BRIDGE_EXE = os.environ.get("ALTIRRA_BRIDGE_EXE", f"{BRIDGE}/AltirraBridgeServer.exe").replace("\\", "/")
PLAN = f"{NOSTY}/results/ntsc_isolated_main/plan.json"
