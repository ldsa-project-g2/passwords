.PHONY: experiments
N_RUNS = 10


experiments:
	run=1 ; while [ $$run -le $(N_RUNS) ] ; do \
		./main_script.py --storage-backend=nfs > nfs-run.$$run.out ; \
		((run = run + 1)) ; \
	done

	run=1 ; while [ $$run -le $(N_RUNS) ] ; do \
		./main_script.py --storage-backend=hdfs > hdfs-run.$$run.out ; \
		((run = run + 1)) ; \
	done
