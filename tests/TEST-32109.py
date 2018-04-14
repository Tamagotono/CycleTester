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
test_window.header.lines[1] = "Test version 1.1b"
test_window.header.update_all_lines()

ontime, offtime = LCDcycleTest.format(pulse_width_ms = PULSE_WIDTH_ms, duty_cycle=DUTY_CYCLE, on_time_ms=ON_TIME_ms, off_time_ms=OFF_TIME_ms)

cycle_num = 0
while cycle_num < NUMBER_OF_CYCLES:
    LCDcycleTest.cycle(ontime, offtime)
    LCDcycleTest.status.line[1] = "Cycle number %d of %d" %(NUMBER_OF_CYCLES-cycle_num, NUMBER_OF_CYCLES)
    LCDcycleTest.status.update_line(1)
    cycle_num += 1
    
