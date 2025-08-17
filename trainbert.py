#!/usr/bin/env python3
import sys, re, glob, shutil, os
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import TrainingArguments, Trainer
from datasets import Dataset, DatasetDict
from natsort import natsorted

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

def main():

  global tokenizer, label2id, id2label

  trnfn, valfn, tstfn = None, None, None
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
  tokenized_datasets = {}
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
      output_dir="./run",
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

    for oldcheckpoint in glob.glob("run/checkpoint-*"):
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
    checkpoints = natsorted(glob.glob("run/checkpoint-*"))
    print("checkpoints: "+",".join(checkpoints))
    if len(checkpoints) == 0:
      raise Exception("no checkpoints")
    if os.path.exists("run/checkpoint-last"):
      shutil.rmtree("run/checkpoint-last")
    shutil.copytree(checkpoints[-1],"run/checkpoint-last")
  
main()
