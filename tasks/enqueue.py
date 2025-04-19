"""Loop skript co se bude pouštět každou chvíli (asi jednou za minutu)"""
import TaskUtils
import time

tasks = TaskUtils.get_task_list()
for task in tasks:
    task_interval = int(TaskUtils.get_task_config(task)['Interval'])
    if (
        TaskUtils.get_task_last_run_timestamp(task) + (task_interval * 60) < int(time.time()) and
        not TaskUtils.is_task_running(task) and
        not TaskUtils.is_task_queued(task)
    ):
        TaskUtils.enqueue_task(task)


