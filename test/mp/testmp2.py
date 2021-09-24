import time
from concurrent.futures import ProcessPoolExecutor,as_completed


def fib(n):
    if n < 3:
        return 1
    return fib(n - 1) + fib(n - 2)


start_time = time.time()
executor = ProcessPoolExecutor(max_workers=4)
task_list = [executor.submit(fib, n) for n in range(3, 35)]
process_results = [task.result() for task in as_completed(task_list)]
print(process_results)
print("ProcessPoolExecutor time is: {}".format(time.time() - start_time))