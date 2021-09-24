import time
from collections import OrderedDict
from concurrent.futures import (
    ThreadPoolExecutor, as_completed
)


def get_thread_time(times):
    time.sleep(times)
    return times


start = time.time()
executor = ThreadPoolExecutor(max_workers=4)
task_list = [executor.submit(get_thread_time, times) for times in [2, 3, 1, 4]]
task_to_time = OrderedDict(zip(["task1", "task2", "task3", "task4"],[2, 3, 1, 4]))
task_map = OrderedDict(zip(task_list, ["task1", "task2", "task3", "task4"]))

for result in as_completed(task_list):
    task_name = task_map.get(result)
    print("{}:{}".format(task_name,task_to_time.get(task_name)))