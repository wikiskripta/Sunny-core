"""Démon skript běžící na pozadí a zpracovávající frontu úkonů"""
import TaskUtils
import time

while True:
    task = TaskUtils.get_next_nonrunning_task_from_queue()
    if (task is None):
        print("Nothing in queue, sleeping for 60 seconds...")
        time.sleep(60) # Sleep for 1 minute
        continue
    
    print("Starting task " + task)
    TaskUtils.set_task_as_running(task)
    
    task_config = TaskUtils.get_task_config(task)
    task_interval = task_config['Interval'];
    enqueuing_enabled = task_config['QueueFillingEnabled'];
    dequeuing_enabled = task_config['QueueProcessingEnabled'];

    if (enqueuing_enabled == 'true'):
        TaskUtils.run_task_queue_filling(task)
    else:
        print("Filling task queue is disabled, skipping...")
    
    if (dequeuing_enabled == 'true'):
        TaskUtils.run_task_queue_processing(task)
    else:
        print("Processing task queue is disabled, skipping...")
    
    TaskUtils.dequeue_task(task)
    TaskUtils.set_task_as_finished(task)
    TaskUtils.update_task_last_run_timestamp(task)
    print("Task finished")
