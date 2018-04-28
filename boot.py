# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import gc
#import webrepl
#webrepl.start()
gc.collect()

import sys
mypath = ['/flash/lib', '/flash/tests', '/sd', '/sd/tests']
for folder in mypath:
    sys.path.append(folder)
