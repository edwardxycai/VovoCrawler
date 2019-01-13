# coding: utf8
# p.py

import os
import sys
import math
import time
import fire
from concurrent.futures import ProcessPoolExecutor, wait
# import web_scrap.py

# add_done_callback(fn)
# Attaches the callable fn to the future. fn will be called, with the future as its only argument,
#  when the future is cancelled or finishes running.
#
# Added callables are called in the order that they were added
#  and are always called in a thread belonging to the process that added them.
#  If the callable raises an Exception subclass, it will be logged and ignored.
#  If the callable raises a BaseException subclass, the behavior is undefined.

# submit(fn, *args, **kwargs)
# Schedules the callable, fn, to be executed as fn(*args **kwargs)
#  and returns a Future object representing the execution of the callable.
#
# with ThreadPoolExecutor(max_workers=1) as executor:
#     future = executor.submit(pow, 323, 1235)
#     print(future.result())


# 分割子任务
def each_task(n):
    # 按公式计算圆周率
    s = 0.0
    for i in range(n):
        s += 1.0/(i+1)/(i+1)
    pi = math.sqrt(6*s)
    # os.getpid可以获得子进程号
    sys.stdout.write("process %s n=%d pi=%s\n" % (os.getpid(), n, pi))
    return pi


def run(process_num, *ns):  # 输入多个n值，分成多个子任务来计算结果
    # 实例化进程池，process_num个进程
    executor = ProcessPoolExecutor(process_num)
    start = time.time()
    fs = []  # future列表
    for n in ns:
        fs.append(executor.submit(each_task, int(n)))  # 提交任务
    wait(fs)  # 等待计算结束
    end = time.time()
    duration = end - start
    print("total cost: %.2fs" % duration)
    executor.shutdown()  # 销毁进程池


# if __name__ == '__main__':
#     fire.Fire(run(5, 5000000, 5001000, 5002000, 5003000, 5004000))
