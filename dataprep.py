#!/usr/bin/env python3
import re

infn = "hpl.sents.txt"
instr = open(infn)
outfn = "hpl.sents.tokstags.txt"
outstr = open(outfn,"w")

for ln in instr:
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
      print(normtok + "\t" + punctag, file=outstr)
