import concurrent.futures
import requests  # This is not standard library
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, wait
import os
import sys
import math
import time
import fire

urls = [
        'https://docs.python.org/3/library/ast.html',
        'https://docs.python.org/3/library/abc.html',
        'https://docs.python.org/3/library/time.html',
        'https://docs.python.org/3/library/os.html',
        'https://docs.python.org/3/library/sys.html',
        'https://docs.python.org/3/library/io.html',
        'https://docs.python.org/3/library/pdb.html',
        'https://docs.python.org/3/library/weakref.html']


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


def run(thread_num, *ns):  # 输入多个n值，分成多个子任务来计算结果
    # 实例化进程池，process_num个进程
    executor = ThreadPoolExecutor(thread_num)
    start = time.time()
    fs = []  # future列表
    for n in ns:
        fs.append(executor.submit(each_task, int(n)))  # 提交任务
    wait(fs)  # 等待计算结束
    end = time.time()
    duration = end - start
    print("total cost: %.2fs" % duration)
    executor.shutdown()  # 销毁进程池


def get_content(url):
    return requests.get(url).text


def scrap():
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        future_to_url = {executor.submit(get_content, url): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
                print('%r page length is %d' % (url, len(data)))
                fire.Fire(run(5, 5000000, 5001000, 5002000, 5003000, 5004000))
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))


if __name__ == '__main__':
    scrap()
