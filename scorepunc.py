#!/usr/bin/env python3
import sys
for fn in sys.argv[1:]:
  print(f"read {fn}")
  fh = open(fn)
  typedispo = {}
  for ln in fh:
    if len(ln.strip()) == 0: continue
    word, reftag, hyptag = ln.strip().split()
    if reftag not in typedispo:
      typedispo[reftag] = { "tot":0 }
    if hyptag not in typedispo[reftag]:
      typedispo[reftag][hyptag] = 0
    typedispo[reftag]["tot"] += 1
    typedispo[reftag][hyptag] += 1
  for type in sorted(typedispo.keys()):
    cols = []
    cols.append(type)
    cols.append(str(typedispo[type]["tot"]))
    for dispo in sorted(typedispo[type].keys()):
      if dispo == "tot": continue
      cols.append(dispo+"="+str(typedispo[type][dispo]))
    cols.append(str(int(100*((typedispo[type][type] if type in typedispo[type] else 0)/typedispo[type]["tot"])+0.5))+"%")
    print("\t".join(cols))
