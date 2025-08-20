#!/usr/bin/env python3
import sys, re, glob, shutil, os
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import TrainingArguments, Trainer
from transformers import pipeline
from datasets import Dataset, DatasetDict
from natsort import natsorted
import torch

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
  tokenized = tokenizer(example["tokens"], is_split_into_words=True, truncation=True, padding='max_length', max_length=512)
  word_ids = tokenized.word_ids()  # map tokens to word indices
  aligned_labels = []
  for word_idx in word_ids:
    if word_idx is None:
      aligned_labels.append(-100)
    else:
      aligned_labels.append(label2id[example["tags"][word_idx]])
  tokenized["labels"] = aligned_labels
  #print("foo: "+str(len(tokenized.word_ids()))+","+str(len(tokenized["labels"])))
  return tokenized

def tagtokens(model,tokenizer,tokens):
  
  encodings = tokenizer(
    tokens,
    is_split_into_words=True,
    return_tensors="pt",
    truncation=True,       # cut off anything past max_length
    max_length=512,        # enforce the 512-token limit
    padding="max_length" 
  )

  with torch.no_grad():
    outputs = model(**encodings)

  logits = outputs.logits
  pred_ids = torch.argmax(logits, dim=-1)

  # Map back to labels
  subword_pred_labels = [model.config.id2label[p.item()] for p in pred_ids[0]]
  subword_to_word = word_ids = encodings.word_ids(batch_index=0)

  word_pred_labels = ["_" for tok in tokens]
  for i in range(len(subword_to_word)):
    if subword_to_word[i] != None:
      word_pred_labels[subword_to_word[i]] = subword_pred_labels[i]

  #for i in range(len(tokens)):
  #  print(tokens[i]+"="+word_pred_labels[i])

  return word_pred_labels
 
def main():

  global tokenizer, label2id, id2label

  trnfn, valfn, tstfn, inferoutfn = None, None, None, None
  quickmode = False
  av = sys.argv[1:]
  ac = 0
  while ac < len(av):
    if av[ac][0] != '-': raise Exception("nonflag: "+av[ac])
    elif av[ac] == "-q": quickmode = True
    elif ac+1 == len(av) or av[ac+1][0] == '-': raise Exception("novalfor: "+av[ac])
    elif av[ac] == "-trn": ac += 1; trnfn = av[ac]
    elif av[ac] == "-val": ac += 1; valfn = av[ac]
    elif av[ac] == "-tst": ac += 1; tstfn = av[ac]
    elif av[ac] == "-out": ac += 1; inferoutfn = av[ac]
    else: raise Exception("unkflag: "+av[ac])
    ac += 1
  
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
  tokenized_datasets = { "trn":None, "val":None, "tst":None }
  for setname in datasets:
    if datasets[setname] == None:
      continue
    print("tokenize "+setname)
    tokenized_datasets[setname] = datasets[setname].map(tokenize_and_align_labels)
    tokenized_datasets[setname] = tokenized_datasets[setname].remove_columns(datasets[setname].column_names)
    print(str(tokenized_datasets[setname]))

  # training a model?
  if tokenized_datasets["trn"] != None and tokenized_datasets["val"] != None:

    print("modelobj")
    model = AutoModelForTokenClassification.from_pretrained(
      "bert-base-uncased",
      num_labels=len(labels),
      id2label=id2label,
      label2id=label2id
    )
  
    print("trainargs")
    trainargs = TrainingArguments(
      output_dir="./run/bert",
      eval_strategy=("steps" if quickmode else "epoch"),
      save_strategy=("steps" if quickmode else "epoch"),
      learning_rate=5e-5,
      per_device_train_batch_size=16,
      per_device_eval_batch_size=16,
      num_train_epochs=(1 if quickmode else 3),
      max_steps=(50 if quickmode else -1),
      weight_decay=0.01,
      save_steps = 25, #only applicable in quickmode
      eval_steps = 25, #only applicable in quickmode
    )

    for oldcheckpoint in glob.glob("run/bert/checkpoint-*"):
      print("del old: "+oldcheckpoint)
      shutil.rmtree(oldcheckpoint)
  
    print("train")
    trainer = Trainer(
      model=model,
      args=trainargs,
      train_dataset=tokenized_datasets["trn"],
      eval_dataset=tokenized_datasets["val"],
      tokenizer=tokenizer,
    )
    trainer.train()

    # copy last checkpoint to checkpoint-latest
    checkpoints = natsorted(glob.glob("run/bert/checkpoint-*"))
    print("checkpoints: "+",".join(checkpoints))
    if len(checkpoints) == 0:
      raise Exception("no checkpoints")
    shutil.copytree(checkpoints[-1],"run/bert/checkpoint-last")

  # inference?
  if datasets["tst"] != None:
    print("inference")
    if inferoutfn == None:
      outstream = sys.stdout
    else:
      outstream = open(inferoutfn,"w")
    # set up tagger
    tagger = pipeline("token-classification", model="run/bert/checkpoint-last", tokenizer=tokenizer, aggregation_strategy="none")
    # sample pg
    sampleinput="it was a dark and stormy night suddenly a shot rang out the maid screamed a door slammed then a pirate ship appeared on the horizon llanfairpwllgwyngyllgogerychwyrndrobwllllantysiliogogogoch"
    samplewordlist = sampleinput.split()
    model = AutoModelForTokenClassification.from_pretrained("run/bert/checkpoint-last")
    sampletaglist = tagtokens(model,tokenizer,samplewordlist)
    print(" ".join(samplewordlist[i]+":"+sampletaglist[i] for i in range(len(samplewordlist))))
    # infererence set
    pgnum = 0
    for pg in datasets["tst"]:
      wordlist = pg["tokens"]
      reftags = pg["tags"]
      hyptags = tagtokens(model,tokenizer,wordlist)
      for i in range(len(wordlist)):
        print("\t".join([wordlist[i],reftags[i],hyptags[i]]),file=outstream)
      print("",file=outstream)
      pgnum += 1
      if re.match(r'^[125]0*$',str(pgnum)):
        print("did "+str(pgnum))
    print("did "+str(pgnum)+"; done")

main()
