# TEST_NAME_1 = "32109r6 Cycle Test"
# TEST_NAME_2 = "Version 2.1" #4/17/2018 JBB
#
import cycleTest
header = cycleTest.test_window.header

header.lines[1] = "32109 Rev6 Test"
header.lines[2] = "Test version 1.1b"
header.update_all_lines()




Round1 = cycleTest.Test(on_time=20, off_time=100, cycles=1000,
                        periodic_function=dwell, func_param=300, func_call_freq=100)

Round2 = cycleTest.Test(pulse_width_ms=2000, duty_cycle=20, cycles=100)



def dwell(ms, on=True):
    if on == True:
        cycleTest.cycle(on_time_ms=ms, off_time_ms=0)
    else:
        cycleTest.cycle(on_time_ms=0, off_time_ms=ms)





if __name__ == "32109r6":
    Round1.begin_test()
    Round2.begin_test()