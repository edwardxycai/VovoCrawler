
import logging
import threading
import time
import requests

urls = [
        'https://docs.python.org/3/library/ast.html',
        'https://docs.python.org/3/library/abc.html',
        'https://docs.python.org/3/library/time.html',
        'https://docs.python.org/3/library/os.html',
        'https://docs.python.org/3/library/sys.html',
        'https://docs.python.org/3/library/io.html',
        'https://docs.python.org/3/library/pdb.html',
        'https://docs.python.org/3/library/weakref.html']

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s'
                    )

items = open('pymulti.txt', 'a+', encoding="utf-8")


def get_content(i):
    res = requests.get(urls[i])
    res.encoding = "utf-8"
    return res


def worker(i):
    logging.debug('Starting')
    res = get_content(i)
    # res.encoding = "utf-8"
    items.write("".join(res.text))
    # time.sleep(2)
    logging.debug('Exiting')


def my_service():
    logging.debug('Starting')
    # time.sleep(3)
    logging.debug('Exiting')


if __name__ == "__main__":
    start = time.process_time()
    t_list = list()
    for i in range(0, 8):
        t = threading.Thread(target=worker, name="worker"+str(i), args=(i,))  # use default name
        t_list.append(t)
        t.start()

    while True:
        num = 9 - threading.active_count()  # 1 main thread + 8 worker threads
        end = time.process_time()
        # print("\n", num, "\n")
        if num > 0:
            for i in range(0, num):
                t = threading.Thread(target=worker, name="workerXXX"+str(end), args=(i,))
                t_list.append(t)
                t.start()

        end = time.process_time()

        if end - start > 10:
            if threading.active_count() > 1:
                time.sleep(5)
            break

    items.close()

