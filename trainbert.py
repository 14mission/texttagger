#!/usr/bin/env python3
import sys, re
from transformers import AutoTokenizer, AutoModelForTokenClassification
from datasets import Dataset, DatasetDict

tokenizer = None
label2id = None

def loaddata(fn,labels):
  print(f"read {fn}")
  fh = open(fn)
  pglist = []
  curpgtoks = []
  curpglbls = []
  for ln in fh:
    if ln.strip() == "":
      if len(curpgtoks) > 0:
        pglist.append( { "tokens": curpgtoks.copy(), "tags": curpglbls.copy() } )
        curpgtoks = []
        curpglbls = []
    else:
      tok, lbl = ln.strip().split("\t")
      curpgtoks.append(tok)
      curpglbls.append(lbl)
      if lbl not in labels:
        labels.append(lbl)
  if len(curpgtoks) > 0:
    pglist.append( { "tokens": curpgtoks.copy(), "tags": curpglbls.copy() } )
  print("pglist len: "+str(len(pglist)))
  return Dataset.from_list(pglist)

def tokenize_and_align_labels(example):
  tokenized = tokenizer(example["tokens"], is_split_into_words=True, truncation=True)
  word_ids = tokenized.word_ids()  # map tokens to word indices
  aligned_labels = []
  for word_idx in word_ids:
    if word_idx is None:
      aligned_labels.append(-100)
    else:
      aligned_labels.append(label2id[example["tags"][word_idx]])
  tokenized["labels"] = aligned_labels
  return tokenized

def main():

  global tokenizer, label2id, id2label

  trnfn, valfn, tstfn = None, None, None
  av = sys.argv[1:]
  ac = 0
  while ac < len(av):
    if av[ac][0] != '-': raise Exception("nonflag: "+av[ac])
    elif ac+1 == len(av) or av[ac+1][0] == '-': raise Exception("novalfor: "+av[ac])
    elif av[ac] == "-trn": ac += 1; trnfn = av[ac]
    elif av[ac] == "-val": ac += 1; valfn = av[ac]
    elif av[ac] == "-tst": ac += 1; tstfn = av[ac]
    else: raise Exception("unkflag: "+av[ac])
    ac += 1
  if valfn == None: raise Exception("need -val VALFN")
  if trnfn == None: raise Exception("need -trn TRNFN")
  #if tstfn == None: raise Exception("need -tst TSTFN")
  
  # load data
  labels = []
  datasets = { "trn":None, "val":None, "tst":None }
  if trnfn != None: datasets["trn"] = loaddata(trnfn, labels)
  if valfn != None: datasets["val"] = loaddata(valfn, labels)
  if tstfn != None: datasets["tst"] = loaddata(tstfn, labels)
  print("labels: "+",".join(labels))
  label2id = {l: i for i, l in enumerate(labels)}
  id2label = {i: l for l, i in label2id.items()}
  
  # tokenize
  tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
  tokenized_datasets = {}
  for setname in datasets:
    if datasets[setname] == None:
      continue
    print("tokenize "+setname)
    tokenized_datasets[setname] = datasets[setname].map(tokenize_and_align_labels)
    print(str(tokenized_datasets[setname]))

  print("done")
  
  
  #model = AutoModelForTokenClassification.from_pretrained(
  #    "bert-base-uncased",
  #    num_labels=len(label_list)
  #)

main()
