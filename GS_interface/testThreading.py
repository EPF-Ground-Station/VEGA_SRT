# -*- coding: utf-8 -*-
"""
Created on Sun Jul 30 15:02:43 2023

@author: lgtle
"""

import threading
i = 0

def thread_func() :
    global i
    while True:
        i += 1


if __name__ == "__main__":
    daemon = threading.Thread(target = thread_func, daemon=True)
    daemon.start()

    print("Press ENTER to stop the program : ")
    print(input())

    print(f"Exiting, final value of i : {i}")
