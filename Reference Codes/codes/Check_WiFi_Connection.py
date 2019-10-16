# -*- coding: utf-8 -*-
"""
Created on Sat Nov 17 21:12:47 2018

@author: Shuyang
"""

import os
import time


def Internet_Check():
    status = os.system("ping www.google.com ")
    if status:
        return False
    else:
        return True


while not Internet_Check():
    print("No connection")
    time.sleep(4)


print("connected")
#os.system("start"+"path")      # for linux/Mac OS
#os.startfile("path")           # for windows, the file/program opened by os.startfile can't be closed by function call












