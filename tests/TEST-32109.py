# TEST_NAME_1 = "32109r6 Cycle Test"
# TEST_NAME_2 = "Version 1.1" #2/7/2018 JBB
#
import LCDcycleTest

NUMBER_OF_CYCLES = const(1000)
PULSE_WIDTH_ms = const(3000) #enter number in mS
DUTY_CYCLE = const(90) #enter duty cycle in percent (%)
#
# # If PULSE_WIDTH = "0" then the following values will be used
ON_TIME_ms  = const(4) #enter number in mS
OFF_TIME_ms = const(4) #enter number in mS
#
#
# INVERTED = const(0) #1 = active Low, 0 = active High
#
#
#
# START_CONDITION = "ON"
# END_CONDIOTION = "OFF"

test_window.header.lines[1] = "32109 Rev6 Test"
test_window.header.lines[2] = "Test version 1.1b"
test_window.header.update_all_lines()

Round1 = LCDcycleTest.Test(on_time=20, off_time=100, cycles=1000, periodic_function=dwell, func_param=300, 100)



def dwell(ms, on=True):
    LCDcycleTest.cycle(on_time_ms=ms,on_time_ms=0)
