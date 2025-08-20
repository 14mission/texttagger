all: run/hpl.sents.tokstags.tst.infer.scoring.txt

run/hpl.sents.tokstags.val.txt: run/hpl.sents.tokstags.trn.txt
run/hpl.sents.tokstags.tst.txt: run/hpl.sents.tokstags.trn.txt
run/hpl.sents.tokstags.trn.txt: hpl.sents.txt dataprep.py run/placeholder.txt
	python3 ./dataprep.py -i hpl.sents.txt -val run/hpl.sents.tokstags.val.txt -tst run/hpl.sents.tokstags.tst.txt -trn run/hpl.sents.tokstags.trn.txt

run/placeholder.txt:
	mkdir run
	touch run/placeholder.txt

# add -q for quick test
run/bert/checkpoint-last/config.json: run/hpl.sents.tokstags.trn.txt run/hpl.sents.tokstags.val.txt run/bert/placeholder.txt
	python3 ./trainbert.py -trn run/hpl.sents.tokstags.trn.txt -val run/hpl.sents.tokstags.val.txt

run/bert/placeholder.txt:
	mkdir run/bert
	touch run/bert/placeholder.txt

run/hpl.sents.tokstags.tst.infer.bert.txt: run/bert/checkpoint-last/config.json trainbert.py
	python3 ./trainbert.py -tst run/hpl.sents.tokstags.tst.txt -out run/hpl.sents.tokstags.tst.infer.bert.txt

run/hpl.sents.tokstags.tst.infer.scoring.txt: run/hpl.sents.tokstags.tst.infer.bert.txt scorepunc.py
	python3 ./scorepunc.py run/hpl.sents.tokstags.tst.infer.bert.txt > run/hpl.sents.tokstags.tst.infer.scoring.txt
