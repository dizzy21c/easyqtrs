import time
from concurrent.futures import ThreadPoolExecutor

# https://www.cnblogs.com/FG123/p/9704233.html
def get_thread_time(times):
    time.sleep(times)
    return times

# 创建线程池  指定最大容纳数量为4
executor = ThreadPoolExecutor(max_workers=4)
# 通过submit提交执行的函数到线程池中
task1 = executor.submit(get_thread_time, (1))
task2 = executor.submit(get_thread_time, (2))
task3 = executor.submit(get_thread_time, (3))
task4 = executor.submit(get_thread_time, (4))
print("task1:{} ".format(task1.done()))
print("task2:{}".format(task2.done()))
print("task3:{} ".format(task3.done()))
print("task4:{}".format(task4.done()))
time.sleep(2.5)
# print('after 2.5s {}'.format('-'*20))
# print("task1-1:{} ".format(task1.done()))
# print("task2-1:{}".format(task2.done()))
# print("task3-1:{} ".format(task3.done()))
# print("task4-1:{}".format(task4.done()))
done_map = {
    "task1":task1.done(),
    "task2":task2.done(),
    "task3":task3.done(),
    "task4":task4.done()
}
# 2.5秒之后，线程的执行状态
for task_name,done in done_map.items():
    # if done:
    print("{}:completed {}".format(task_name, done))