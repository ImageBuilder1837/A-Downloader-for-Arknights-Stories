import os
from lib import *
from queue import Queue
from threading import Thread, Lock


# ===============基石函数===============


def pprint(string: str, lock: Lock):
    '''防止多线程输出混淆'''

    lock.acquire()
    print(string)
    lock.release()


# ===============底层函数===============


def cpt_thread(dic: dict, num: int, que: Queue, lock: Lock):
    '''自动领取任务的线程函数'''

    while ans := que.get():
        if ans == "<quit>":
            pprint(f"Thread-{num}: Quit", lock)
            que.task_done()
            break

        type_, chapter = ans
        pprint(f"Thread-{num}: Downloading {chapter}", lock)
        download_chapter(chapter, dic, type_)
        pprint(f"Thread-{num}: Successfully downloaded {chapter}", lock)
        que.task_done()


# ===============终端函数===============


def main():
    dic = get_story_dic()
    dic.update(get_secret_dic())
    type_list, titles = get_input(dic)

    que = Queue()
    for type_ in type_list:
        if not os.path.exists(type_):
            os.mkdir(type_)
        for chapter in titles[type_]:
            que.put((type_, chapter))

    lock = Lock()
    for num in range(1, amount + 1):
        que.put("<quit>")
        Thread(target=cpt_thread, args=(dic, num, que, lock)).start()

    que.join()
    print("\nAll tasks done")


if __name__ == "__main__":
    main()