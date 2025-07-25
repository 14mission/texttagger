#!/usr/bin/env python3
import re, sys, random

infn, outtrnfn, outvalfn, outtstfn = None, None, None, None
batchsize = 100
valfrac = 0.01
tstfrac = 0.1
av = sys.argv[1:]
ac = 0
while ac < len(av):
  if av[ac][0] != '-': raise Exception("nonflag: "+av[ac])
  elif av[ac] == "-h": print("dataprep.py -i INFN -trn TRNFN -val VALFN -tst TSTFN"); sys.exit(0)
  elif ac+1 == len(av) or av[ac+1][0] == '-': raise Exception("novalfor: "+av[ac])
  elif av[ac] == "-i": ac += 1; infn = av[ac]
  elif av[ac] == "-trn": ac += 1; outtrnfn = av[ac]
  elif av[ac] == "-val": ac += 1; outvalfn = av[ac]
  elif av[ac] == "-tst": ac += 1; outtstfn = av[ac]
  else: raise Exception("unkflag: "+av[ac])
  ac += 1
if infn == None: raise Exception("need -i INFN")
if outvalfn == None: raise Exception("need -val VALFN")
if outtrnfn == None: raise Exception("need -trn TRNFN")
if outtstfn == None: raise Exception("need -tst TSTFN")

instrm = open(infn)
outvalstrm = open(outvalfn,"w") 
outtrnstrm = open(outtrnfn,"w")
outtststrm = open(outtstfn,"w")

random.seed(666)

linenum = 0
writeto = None
for ln in instrm:
  if linenum % batchsize == 0:
    rndnum = random.randrange(1000) * 0.001
    if rndnum < valfrac:
      writeto = "val"
    elif rndnum < valfrac + tstfrac:
      writeto = "tst"
    else:
      writeto = "trn"
  for tok in ln.split():
    normtok = re.sub(r'"|^\'|\'$','',tok)
    if re.match(r'^.*?\[\.:;-]+$', normtok): 
      punctag = "PD"
    elif re.match(r'^.*?\?$', normtok):
      punctag = "QM"
    elif re.match(r'^.*?\!$', normtok):
      punctag = "XP"
    elif re.match(r'^.*?,$', normtok):
      punctag = "CO"
    else:
      punctag = "NO"
    normtok = normtok.lower()
    normtok = re.sub(r'(^\W+|\W+$)','',normtok)
    if len(normtok) > 0:
      print(normtok + "\t" + punctag,
       file=(outvalstrm if writeto == "val" else (outtststrm if writeto == "tst" else outtrnstrm)))
  linenum += 1
