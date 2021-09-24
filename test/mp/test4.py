import time
from concurrent.futures import ThreadPoolExecutor


def get_thread_time(times):
    time.sleep(times)
    return times


start = time.time()
executor = ThreadPoolExecutor(max_workers=4)

i = 1
for result in executor.map(get_thread_time,[4,3,2,1]):
    print("task{}:{}".format(i, result))
    i += 1