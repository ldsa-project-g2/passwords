.PHONY: experiments
N_RUNS = 10
FINAL_STORAGE_SOLUTION = "nfs"
MAX_WORKERS = 10
WORKER_STEP = 2
WORKER_START = 1


experiments:
	run=1 ; while [ $$run -le $(N_RUNS) ] ; do \
		./main_script.py --storage-backend=nfs > nfs-run.$$run.out ; \
		((run = run + 1)) ; \
	done

	run=1 ; while [ $$run -le $(N_RUNS) ] ; do \
		./main_script.py --storage-backend=hdfs > hdfs-run.$$run.out ; \
		((run = run + 1)) ; \
	done


.PHONY: worker-experiments

worker-experiments:
	run=$(WORKER_START) ; while [ $$run -le $(N_RUNS) ] ; do \
		$(SPARK_HOME)/sbin/stop-all.sh && \
		sleep 5 && \
		./set-spark-workers $$run && \
		$(SPARK_HOME)/sbin/start-all.sh && \
		./main_script.py --storage-backend=$(FINAL_STORAGE_SOLUTION) \
			> worker-experiment.$(FINAL_STORAGE_SOLUTION).$$run.out ; \
		((run = run + $(WORKER_STEP))) ; \
	done
