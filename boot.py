# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()


import gc
gc.collect()

import sys
sys.path[1:3] = '/flash/lib', '/flash/tests', '/sd'
