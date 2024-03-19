from SRT_inline import *
from random import randint
from time import sleep


SRT.connectAPM(False)
i = 0
while i <60 : 

    SRT.pointAzAlt(randint(20, 359), randint(15, 85))
    time.sleep(120)
    i += 1

SRT.disconnect()