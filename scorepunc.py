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
  allcatscount = 0
  allcatscorrect = 0
  for type in sorted(typedispo.keys()):
    cols = []
    cols.append(type)
    cols.append(str(typedispo[type]["tot"]))
    catcount = typedispo[type]["tot"]
    catcorrectcount = typedispo[type][type] if type in typedispo[type] else 0
    cols.append(str(int(100*catcorrectcount/catcount+0.5))+"%")
    allcatscount += catcount
    allcatscorrect += catcorrectcount
    for dispoandcount in sorted(typedispo[type].items(), key=lambda item: item[1], reverse=True):
      dispo, count = dispoandcount
      if dispo == "tot": continue
      cols.append(dispo+"="+str(count))
    print("\t".join(cols))
  print("ALL\t"+str(allcatscount)+"\t"+str(int(100*allcatscorrect/allcatscount+0.5))+"%\tself="+str(allcatscorrect)+"\tother="+str(allcatscount-allcatscorrect))
