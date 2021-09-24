import time
import os

# os.getpid()   获取自己进程的ID号
# os.getppid()  获取自己进程的父进程的ID号

from multiprocessing import Process

def func():
    print("*"*10)
    time.sleep(1)
    print("子进程ID>>>", os.getpid())
    print("子进程的父进程ID>>>", os.getppid())
    print("~"*10)

if __name__ == '__main__':
    p = Process(target=func,)
    p.start()
    print("@"*10)
    print("父进程ID>>>", os.getpid())
    print("父进程的父进程ID>>>", os.getppid())
    print("#"*10)
    
# @@@@@@@@@@
# 父进程ID>>> 9040
# 父进程的父进程ID>>> 6328
# ##########
# **********
# 子进程ID>>> 6872
# 子进程的父进程ID>>> 9040
# ~~~~~~~~~~

# 举例说明