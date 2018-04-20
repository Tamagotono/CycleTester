# TEST_NAME_1 = "32109r6 Cycle Test"
# TEST_NAME_2 = "Version 2.1" #4/17/2018 JBB
#
# import cycleTest
#
# print("My __name__ is " + __name__)
#
# ps_relay = cycleTest.Relay(2)
# test_UI = cycleTest.UI()
#
from cycleTest import *

ps_relay = Relay(2)

def dwell(ms, on=True):
    if on is True:
        cycle(on_time_ms=ms, off_time_ms=0, relay=ps_relay)
    else:
        cycle(on_time_ms=0, off_time_ms=ms, relay=ps_relay)

#Round1 = cycleTest.Test(relay=ps_relay, on_time=20, off_time=100, cycles=1000,
 #                       periodic_function=dwell, func_param=300, func_call_freq=100)

Round2 = Test(relay=ps_relay, pulse_width_ms=1111, duty_cycle=22, cycles=100)


header = test_UI.header
parameters = test_UI.parameters

header.lines[1] = "32109 Rev6 Test"
header.lines[2] = "Test version 1.1b"
header.update_all_lines()
#
# print("Round2 = " + str(Round2))
# print("Round2 [0] = " + str(Round2[0]))
# print("Round2 [1] = " + str(Round2[1]))
# print("Round2 [2] = " + str(Round2[2]))
# print("Round2 [3] = " + str(Round2[3]))

parameters.lines[1] = "On Time     = " + prettyTime(Round2[0])
parameters.lines[2] = "Off Time    = " + prettyTime(Round2[1])
parameters.lines[3] = "Pulse Width = " + prettyTime(Round2[2])
parameters.lines[4] = "Duty Cycle  = " + str(Round2[3])
parameters.update_all_lines()

#    Round1.begin_test()
Round2.begin_test()