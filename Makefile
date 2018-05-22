.PHONY: experiments
SHELL := /bin/bash
N_RUNS = 2
FINAL_STORAGE_SOLUTION = "nfs"
MAX_WORKERS = 10
WORKER_STEP = 5
WORKER_START = 5

experiments:
	$(SPARK_HOME)/sbin/stop-all.sh
	sleep 5
	./set-spark-workers.py $(MAX_WORKERS)
	$(SPARK_HOME)/sbin/start-all.sh

	run=1 ; while [[ $$run -le $(N_RUNS) ]] ; do \
		./main_script.py --storage-backend=nfs > nfs-run.$$run.out ; \
		((run = run + 1)) ; \
	done

	run=1 ; while [[ $$run -le $(N_RUNS) ]] ; do \
		./main_script.py --storage-backend=hdfs > hdfs-run.$$run.out ; \
		((run = run + 1)) ; \
	done


.PHONY: worker-experiments

worker-experiments:
	run=$(WORKER_START) ; while [[ $$run -le $(MAX_WORKERS) ]] ; do \
		$(SPARK_HOME)/sbin/stop-all.sh && \
		sleep 5 && \
		./set-spark-workers.py $$run && \
		$(SPARK_HOME)/sbin/start-all.sh && \
		./main_script.py --storage-backend=$(FINAL_STORAGE_SOLUTION) \
			> worker-experiment.$(FINAL_STORAGE_SOLUTION).$$run.out ; \
		((run = run + $(WORKER_STEP))) ; \
	done


clean:
	$(RM) {nfs,dfs}-run.*.out run.*.out
