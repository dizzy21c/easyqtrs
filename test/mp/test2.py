import time
from concurrent.futures import (
    ThreadPoolExecutor, wait
)


def get_thread_time(times):
    time.sleep(times)
    return times


start = time.time()
executor = ThreadPoolExecutor(max_workers=4)
task_list = [executor.submit(get_thread_time, times) for times in [1, 2, 3, 4,5,6,6,6,6,8]]
i = 1
for task in task_list:
    print("task{}:{}".format(i, task))
    i += 1
print(wait(task_list, timeout=2.5))