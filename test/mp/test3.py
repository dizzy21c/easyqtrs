import time
from concurrent.futures import ThreadPoolExecutor


def get_thread_time(times):
    time.sleep(times)
    return times


start = time.time()
executor = ThreadPoolExecutor(max_workers=4)

i = 1
for result in executor.map(get_thread_time,[2,3,1,4]):
    print("task{}:{}".format(i, result))
    i += 1