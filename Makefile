run/hpl.sents.tokstags.val.txt: run/hpl.sents.tokstags.trn.txt
run/hpl.sents.tokstags.tst.txt: run/hpl.sents.tokstags.trn.txt
run/hpl.sents.tokstags.trn.txt: hpl.sents.txt dataprep.py
	python3 ./dataprep.py -i hpl.sents.txt -val run/hpl.sents.tokstags.val.txt -tst run/hpl.sents.tokstags.tst.txt -trn run/hpl.sents.tokstags.trn.txt
