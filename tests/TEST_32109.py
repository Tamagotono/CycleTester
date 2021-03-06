from cycleTest import *

ps_relay = Relay(2)
PW = 123
DS = 25
CYCLES = 88

HEADERLINE1 = "32109 Rev6 Test"
HEADERLINE2 = "Test version 1.1b"




def dwell(ms, on=True):
    if on is True:
        cycle(on_time_ms=ms, off_time_ms=0, relay=ps_relay)
    else:
        cycle(on_time_ms=0, off_time_ms=ms, relay=ps_relay)

#Round1 = cycleTest.Test(relay=ps_relay, on_time=20, off_time=100, cycles=1000,
 #                       periodic_function=dwell, func_param=300, func_call_freq=100)



Round2 = Test(relay=ps_relay, pulse_width_ms=PW, duty_cycle=DS, cycles=CYCLES)


header = test_UI.header
parameters = test_UI.parameters

header.lines[0:1] = [HEADERLINE1]
header.lines[1:2] = [HEADERLINE2]
header.update_all_lines()


update_parameters_pane(*Round2)

#    Round1.begin_test()
Round2.begin_test()