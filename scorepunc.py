#!/usr/bin/env python3
import sys
for fn in sys.argv[1:]:

  # read tsv file
  # lines should be: id \t refcat \t hypcat
  # build: typedispo->refcat->hypcat counts
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

  # longest refcat len
  longestcatlen = 0
  for cat in typedispo.keys():
    if len(cat) > longestcatlen:
      longestcatlen = len(cat)

  # report types and dispos
  print("refcat".ljust(longestcatlen,' ') + "\tn\trecall\thypcats")
  allcatscount = 0
  allcatscorrect = 0
  for typeanddispos in sorted(typedispo.items(), key=lambda item: str(1.0/item[1]["tot"])+item[0]): # sort by typetot desc, type
    type, dispos = typeanddispos
    cols = []
    cols.append(type.ljust(longestcatlen,' '))
    cols.append(str(dispos["tot"]))
    catcount = dispos["tot"]
    catcorrectcount = dispos[type] if type in dispos else 0
    cols.append(str(int(100*catcorrectcount/catcount+0.5))+"%")
    allcatscount += catcount
    allcatscorrect += catcorrectcount
    for dispoandcount in sorted(dispos.items(), key=lambda item: str(1.0/item[1])+item[0]): # sort by dispotypecount desc, type
      dispo, count = dispoandcount
      if dispo == "tot": continue
      cols.append(dispo+"="+str(count))
    print("\t".join(cols))
  print("ALL".ljust(longestcatlen,' ')+"\t"+str(allcatscount)+"\t"+str(int(100*allcatscorrect/allcatscount+0.5))+"%\tself="+str(allcatscorrect)+"\tother="+str(allcatscount-allcatscorrect))
