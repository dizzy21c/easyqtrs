import os
import time
import random
from multiprocessing import Pool

def work(n):
    print('%s run' % os.getpid())   # 进程ID号
    time.sleep(random.random())
    return n**2

if __name__ == '__main__':
    p = Pool(4) # 进程池中从无到有创建三个进程,以后一直是这三个进程在执行任务
    res_l = []
    for i in range(10):
        # res = 
        p.apply_async(work, args=(i,))
        """异步运行,根据进程池中的进程数,每次最多4个子进程在异步执行,并且可以执行不同的任务,传送任意的参数了.
        返回结果之后,将结果放入列表,归还进程,之后再执行新的任务.需要注意的是,进程池中的三个进程不会同时开启或
        者同时结束而是执行完一个就释放一个进程,这个进程就去接收新的任务."""
        # res_l.append(res)

    """异步apply_async用法:如果使用异步提交的任务,主进程需要使用join,等待进程池内任务都处理完,然后可以用get收集结果.
        否则,主进程结束,进程池可能还没来得及执行,也就跟着一起结束了."""
    p.close()   # 不是关闭进程池,而是结束进程池接收任务,确保没有新任务再提交过来.
    p.join()    # 感知进程池中的任务已经执行结束,只有当没有新的任务添加进来的时候,才能感知到任务结束了,所以在join之前必须加上close方法.
    # for res in res_l:
    #     print(res.get())    # 使用get来获取apply_aync的结果,如果是apply,则没有get方法,因为apply是同步执行,立刻获取结果,也根本无需get.

# 进程池的异步调用