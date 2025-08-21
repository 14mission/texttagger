all: run/hpl.sents.tokstags.tst.infer.scoring.txt

run/hpl.sents.tokstags.val.txt: run/hpl.sents.tokstags.trn.txt
run/hpl.sents.tokstags.tst.txt: run/hpl.sents.tokstags.trn.txt
run/hpl.sents.tokstags.trn.txt: hpl.sents.txt dataprep.py run/placeholder.txt
	python3 ./dataprep.py -i hpl.sents.txt -val run/hpl.sents.tokstags.val.txt -tst run/hpl.sents.tokstags.tst.txt -trn run/hpl.sents.tokstags.trn.txt -vf 0.1 -tf 0.1

run/placeholder.txt:
	mkdir run
	touch run/placeholder.txt

# add -q for quick test
run/bertpre/checkpoint-last/config.json: run/hpl.sents.tokstags.trn.txt run/hpl.sents.tokstags.val.txt run/bertpre/placeholder.txt
	python3 ./trainbert.py -trn run/hpl.sents.tokstags.trn.txt -val run/hpl.sents.tokstags.val.txt -mod run/bertpre

run/bertpre/placeholder.txt:
	mkdir run/bertpre
	touch run/bertpre/placeholder.txt

run/hpl.sents.tokstags.tst.infer.bertpre.txt: run/bertpre/checkpoint-last/config.json trainbert.py
	python3 ./trainbert.py -tst run/hpl.sents.tokstags.tst.txt -out run/hpl.sents.tokstags.tst.infer.bertpre.txt -mod run/bertpre


# add -q for quick test
run/bertraw/checkpoint-last/config.json: run/hpl.sents.tokstags.trn.txt run/hpl.sents.tokstags.val.txt run/bertraw/placeholder.txt
	python3 ./trainbert.py -raw -trn run/hpl.sents.tokstags.trn.txt -val run/hpl.sents.tokstags.val.txt -mod run/bertraw

run/bertraw/placeholder.txt:
	mkdir run/bertraw
	touch run/bertraw/placeholder.txt

run/hpl.sents.tokstags.tst.infer.bertraw.txt: run/bertraw/checkpoint-last/config.json trainbert.py
	python3 ./trainbert.py -tst run/hpl.sents.tokstags.tst.txt -out run/hpl.sents.tokstags.tst.infer.bertraw.txt -mod run/bertraw

run/hpl.sents.tokstags.tst.infer.scoring.txt: run/hpl.sents.tokstags.tst.infer.bertpre.txt run/hpl.sents.tokstags.tst.infer.bertraw.txt scorepunc.py
	python3 ./scorepunc.py run/hpl.sents.tokstags.tst.infer.bertpre.txt run/hpl.sents.tokstags.tst.infer.bertraw.txt > run/hpl.sents.tokstags.tst.infer.scoring.txt
