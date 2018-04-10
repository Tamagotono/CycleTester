#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  4 17:13:49 2018
This Rewrite started April 5th, 2018
VERSION 1.1
This is a configurable pulse generator designed for stress-testing PCBAs.
Developed on a generic ESP8266 development board and an ST7735 LCD display.

Display updates are disabled when the on/off times are too short to allow
the display to be updated between state transitions.  Different displays may
be faster and allow the display to be updated at faster switching speeds.
This is not important for the intended purpose, as 56mS states are already
faster than desirable switching rates.

TIP: docs.micropython.org/en/latest/esp8266/esp8266/quickref.html

TODO:
    * Make the test configuration setup a separate file
    * Make the hardware setup a separate file
    * Make a menu to select the test configuration file (in progress)
    * Make a separate function to update the different sections of the display
    * Allow live adjustment of the settings
    * Allow saving of new profiles
    * Add an encoder for navigating the menus. (Soldered to pins 9 and 10)
    * Add Wifi interface for manual control or checking current status
    * Switch to the importlib method of loading variable modules, when this feature is added to uPy. (Not available)

NOTE:
    * Using IO pin 2 for the toggle pin is a bad idea. It cycles multiple times during boot
    * Pin 4 seems to be tied to communications... Need to research for better choice of pins


"""

#import machine, display, time,
import machine, _thread, math
#import m5stack
import utime, machine #Cycle count required imports
from micropython import const
import hardware_config
import gc

tft, btn_a, btn_b, btn_c = hardware_config.M5stack()
machine.freq(160000000)

class UI:
    """
    Args:
        title_size (int): The number of lines for the Title section. Default = 1

        nav_size (int): The number of lines for the Navigation section. Set to 0 for test UIs. Default = 0

        parameter_size (int): The number of lines for the Parameter section. Set to 0 for menu UIs. Default = 4

        status_size (int): The number of lines for the Status section. Set to 0 for menu UIs. Default = 3

        notification_size (int): The number of lines for the Notification section. Default = 1

    Note:
        This is the display for a specific test / menu. All calls to change the
        information on the screen need to go through the GUI2LCD instance.
    """
    global tft

    def __init__(self,
                 title_size: int = 1,
                 nav_size: int = 0,
                 parameter_size: int = 4,
                 status_size: int = 3,
                 notification_size: int = 1,
                 ):

        self.clear()
        tft.font(tft.FONT_DejaVu24)


    def clear(self):
        tft.clear()

    def header():
        FRAME_COLOR = tft.BLUE
        FILL_COLOR = tft.BLUE
        TEXT_COLOR = 0xffffff
        HEIGHT = 60
        text_line_1 = ''
        text_line_2 = ''

        tft.rect(0, 0, 320, HEIGHT, FRAME_COLOR, FILL_COLOR)
        printLCD(TEST_NAME_1, Y=LCDTitle1, Background=BLUE)
        printLCD(TEST_NAME_2, Y=LCDTitle2, Background=BLUE)

    def test_param():
        FRAME_COLOR = tft.BLUE
        FILL_COLOR = tft.BLUE
        TEXT_COLOR = 0xffffff
        HEIGHT = 60
        text_line_1 = ''
        text_line_2 = ''

        tft.rect(0, 0, 320, 20, tft.RED, tft.RED)
        printLCD(TEST_NAME_1, Y=LCDTitle1, Background=BLACK)
        printLCD(TEST_NAME_2, Y=LCDTitle2, Background=BLACK)

    def test_status():
        FRAME_COLOR = tft.BLUE
        FILL_COLOR = tft.BLUE
        TEXT_COLOR = 0xffffff
        HEIGHT = 60
        text_line_1 = ''
        text_line_2 = ''

        tft.rect(0, 0, 320, 20, tft.RED, tft.RED)
        printLCD(TEST_NAME_1, Y=LCDTitle1, Background=BLUE)
        printLCD(TEST_NAME_2, Y=LCDTitle2, Background=BLUE)

    def footer(self):
        tft.rect( 25, 210, 80, 30, tft.RED, tft.BLUE)
        tft.text( 50, 215,   "UP", tft.WHITE, transparent=True)

        tft.rect(120, 210, 80, 30, tft.RED, tft.BLUE)
        tft.text(120, 215, "DOWN", tft.WHITE, transparent=True)

        tft.rect(215, 210, 80, 30, tft.RED, tft.BLUE)
        tft.text(235, 215,  "SEL", tft.WHITE, transparent=True)

    def printLCD(text, X=0, Y=0, bg_color=0x000000, text_color=0xffffff, transparent=True):
        text = str(f'{text}\r')
        tft.textClear(X, Y, text)
        tft.text(X, Y, text, text_color, transparent=True)



class Test:
    """
    Args:

    Note:
        Defines the parameters of the test
    """
    def __init__(self, on_time_ms: int, off_time_ms: int, relay: Relay, button: machine.Signal, display ):
        pass

    def read_current(seconds: int, relay: Relay) -> None:
        printLCD("Enabling DC power", Y=LCDStatusLine1)
        relay.on()
        printLCD("Dwell for " + str(seconds) + " seconds", Y=LCDStatusLine2)
        utime.sleep_ms(seconds * 1000)  # allow time for the readings to stabilize
        printLCD("Take measurement now", Y=LCDStatusLine1, Background=0xaaaa)
        printLCD("Press Button", Y=LCDStatusLine2, Background=0x0)
        printLCD("", Y=LCDStatusLine3, Background=0x0)
        while button.value() == 1:
            utime.sleep_ms(50)
        printLCD("", Y=LCDStatusLine1)
        printLCD("", Y=LCDStatusLine2)
        printLCD("", Y=LCDStatusLine3)
        return

    def kill_power():
        disable()
        printLCD("Power is off", Y=LCDStatusLine1)
        printLCD("load/unload PCBA", Y=LCDStatusLine2)
        printLCD("Press button", Y=LCDStatusLine3)
        while button.value() == 1:
            utime.sleep_ms(50)
        printLCD("", Y=LCDStatusLine1)
        printLCD("", Y=LCDStatusLine2)
        printLCD("", Y=LCDStatusLine3)
        return

    def keep_power_on():
        disable()
        printLCD("Press button to", Y=LCDStatusLine2)
        printLCD("turn power off", Y=LCDStatusLine3)
        while button.value() == 1:
            utime.sleep_ms(50)
        printLCD("", Y=LCDStatusLine1)
        printLCD("", Y=LCDStatusLine2)
        printLCD("", Y=LCDStatusLine3)
        return

    def perform_test():
        updatesDisabled = False

        def updateDisplay(count):
            if updatesDisabled == True:
                return
            printLCD(str(count) + " of " + str(NUMBER_OF_CYCLES), Y=LCDStatusLine2)
            rt = ((ON_TIME_ms + OFF_TIME_ms) * (NUMBER_OF_CYCLES - count))  # rt stands for Remaining Time
            rt = prettyTime(rt, verbose=False)
            printLCD("Left:" + str(rt), Y=LCDStatusLine3)

        printLCD("Test in progress", Y=LCDStatusLine1)
        if ON_TIME_ms < DISPLAY_UPDATE_INTERVAL and OFF_TIME_ms < DISPLAY_UPDATE_INTERVAL:
            printLCD("Updates Disabled", Y=LCDStatusLine2)
            printLCD("Cycles= " + str(NUMBER_OF_CYCLES), Y=LCDStatusLine3)
            updatesDisabled = True
        else:
            updateDisplay(NUMBER_OF_CYCLES)

        displayUpdateDue = utime.ticks_add(utime.ticks_ms(), DISPLAY_UPDATE_INTERVAL)
        displayUpdateRemaining = utime.ticks_diff(utime.ticks_ms(), displayUpdateDue)

        for count in range(NUMBER_OF_CYCLES):
            count += 1
            waiting = True
            deadline = utime.ticks_add(utime.ticks_ms(), +ON_TIME_ms)

            enable()
            while waiting == True:
                msRemaining = utime.ticks_diff(utime.ticks_ms(), deadline)
                if msRemaining <= -1:  # the -1 is to allow for calculation time
                    displayUpdateRemaining = utime.ticks_diff(utime.ticks_ms(), displayUpdateDue)
                    if displayUpdateRemaining >= 0 and msRemaining < -55:  # defer the update if there is not enough time before the next toggle state change
                        updateDisplay(count)
                        displayUpdateDue = utime.ticks_add(utime.ticks_ms(), DISPLAY_UPDATE_INTERVAL)
                else:
                    waiting = False

            disable()
            waiting = True
            deadline = utime.ticks_add(utime.ticks_ms(), +OFF_TIME_ms)
            while waiting == True:
                msRemaining = utime.ticks_diff(utime.ticks_ms(), deadline)
                if msRemaining <= -1:  # the -1 is to allow for calculation time
                    displayUpdateRemaining = utime.ticks_diff(utime.ticks_ms(), displayUpdateDue)
                    if displayUpdateRemaining >= 0 and msRemaining < -55:  # defer the update if there is not enough time before the next toggle state change
                        updateDisplay(count)
                        displayUpdateDue = utime.ticks_add(utime.ticks_ms(), DISPLAY_UPDATE_INTERVAL)
                else:
                    waiting = False

        updateDisplay(count)

class Relay(machine.Signal):
    """
    Notes:
        Adds extra feature to the machine.Signal class

    Adds:
        toggle: Inverts the current state of the pin.
    """
    def __init__(self, gpio_pin_number: int, inverted=False):
        super().__init__(gpio_pin_number, inverted)

    def toggle(self):
        self.value(not self.value())

class Button:
    def __init__(self, gpio_pin_number: int):
        self.gpio_pin = machine.Pin(gpio_pin_number, machine.Pin.IN, machine.Pin.PULL_UP)
    pass

class Encoder:
    pass

class GUI2LCD:
    """
    Args:

    Note:
        Used to convert generic display changes to LCD Driver commands.
        This should make it easier to adapt to various displays.
    """

def prettyTime(milliseconds: int, msPrecision: int=1, verbose: bool=False) -> str:
    """
    Args:
        milliseconds: The value in milliseconds to format
        msPrecision: The number of digits to show for the milliseconds portion of the output.
                     Default = 1
        verbose: If verbose is True, it will output days, hours, minutes, seconds, milliseconds.
                 If verbose is False, it will display only the minimum values needed.
                 Default = False

    Returns: A string with the converted time in human readable format with the precision specified.
    """
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)
    years, weeks = divmod(weeks, 52)

    #time:=str("%1dy %1dw %1dd" % (years, weeks, days))
    time:=str(f'{years} {weeks} {days}')
    if verbose == False:
        if years == 0:
            time=str("%1dw %1dd %1dh" % (weeks, days, hours))
            if weeks == 0:
                time=str("%1dd %1dh %02dm" % (days, hours, minutes))
                if days == 0:
                    time=str("%1dh %02dm %02ds" % (hours, minutes, seconds))
                    if hours == 0:
                        time=str("%02dm %02ds" % (minutes, seconds))
                        if minutes == 0:
                            time=str("%04.2fs" % (seconds+(milliseconds/1000)))
                            if seconds == 0:
                                time=str("%1dms" % (truncate(milliseconds, precision=msPrecision)))
    else:
        time=str("%1dy %1dw %1dd %1dh %02dm %02ds.%3ds" % (years, weeks, days, hours, minutes, seconds, milliseconds))
    return time

def truncate(original_number: float, precision: int=1) -> float:
    """
    Args:
        original_number: The float that you want truncated (not rounded)
        precision: Int defining how many decimal places to truncate at.

    Returns: The original float, but truncated to the specified number of decimal places.
             Default = 1
    """
    precision=int(precision)
    if precision>0:
        multiplier=int(10 ** precision)
        truncated_number = int(original_number * multiplier) / float(multiplier)# left shift, chop, right shift
    else:
        truncated_number = int(original_number)
    return truncated_number

def cycle(on_time_ms: int, off_time_ms: int, relay: Relay) -> None:
    """
    Args:
        on_time_ms (int): The desired time in milliseconds for the ON period of the cycle.
        off_time_ms (int): The desired time in milliseconds for the OFF period of the cycle.
        relay (Relay): The instance of the relay to be acted on.
    Returns:
        None
    """
    relay.on()
    utime.sleep_ms(on_time_ms)
    relay.off()
    utime.sleep_ms(off_time_ms)
    gc.collect()


# --------------- in work ----------
def format(pulse_width_ms: int=1000, duty_cycle:  int=50,
           on_time_ms:     int=250,  off_time_ms: int=100) -> tuple(int, int):
    """
    Args:
        pulse_width_ms: The pulse width in milliseconds.
                        Default = 1000 (1 second)
        duty_cycle: The duty cycle in percent
                    Default = 50%

        on_time_ms: The on time in milliseconds.
                    Default = 250 milliseconds.
        off_time_ms: The off time in milliseconds.
                     Default = 100 milliseconds.

    Returns: The on and off time in milliseconds, computed from the values given.
    Notes:  pulse_width and duty_cycle take priority over any values given for the on_time_ms and off_time_ms.
    """
    if pulse_width_ms != 0:
        on_time_ms = int(pulse_width_ms * (duty_cycle / 100))
        off_time_ms = int(pulse_width_ms - on_time_ms)
    else:
        on_time_ms = int(on_time_ms)
        off_time_ms = int(off_time_ms)
        pulse_width_ms = int(on_time_ms + off_time_ms)
        duty_cycle = trunc(((on_time_ms / pulse_width_ms) * 100), 2)

    time=((on_time_ms + off_time_ms) * NUMBER_OF_CYCLES)  ### <-- should not be here, but not sure where is right...

    printLCD("PW  = " + prettyTime(pulse_width_ms), Y=LCDParamLine1)
    printLCD("DS  = " + str(duty_cycle) + "%", Y=LCDParamLine2)
    printLCD("ON  = " + prettyTime(on_time_ms, 3), Y=LCDParamLine3)
    printLCD("OFF = " + prettyTime(off_time_ms, 3), Y=LCDParamLine4)
    printLCD("Time= "+prettyTime(time, 3), Y=LCDParamLine5 )

    gc.collect()
    return (on_time_ms, off_time_ms)

def load_test_settings(TestConfigFile):
    global  TEST_NAME_1, TEST_NAME_2,\
            NUMBER_OF_CYCLES,\
            PULSE_WIDTH_ms, DUTY_CYCLE,\
            ON_TIME_ms, OFF_TIME_ms,\
            INVERTED

    TestConfig = __import__(TestConfigFile)

    TEST_NAME_1 = TestConfig.TEST_NAME_1
    TEST_NAME_2 = TestConfig.TEST_NAME_2
    NUMBER_OF_CYCLES = TestConfig.NUMBER_OF_CYCLES
    PULSE_WIDTH_ms = TestConfig.PULSE_WIDTH_ms
    DUTY_CYCLE = TestConfig.DUTY_CYCLE
    ON_TIME_ms  = TestConfig.ON_TIME_ms
    OFF_TIME_ms = TestConfig.OFF_TIME_ms
    INVERTED = TestConfig.INVERTED

def m5():
    a = m5stack.ButtonA(callback=button_hander_a)
    b = m5stack.ButtonB(callback=button_hander_b)
    c = m5stack.ButtonC(callback=button_hander_c)


if __name__ == __main__:
    gc.enable()
    gc.collect()

    machine.freq(80000000)
    print("configuring hardware")

    DISPLAY_UPDATE_INTERVAL = const(56)  # Do not set below 56 or the display will not update
    TOGGLE_PIN_1 = const(4)
    # TOGGLE_PIN_2 = const(11)

    buttonPin = const(0)
    ENCODER_PIN_1 = const(9)
    ENCODER_PIN_2 = const(10)

    RED = rgb.color565(255, 0, 0)
    BLUE = rgb.color565(0, 255, 0)
    GREEN = rgb.color565(0, 0, 255)
    BLACK = rgb.color565(0, 0, 0)

    LCDTitle1 = const(0)
    LCDTitle2 = const(10)

    LCDParamLine1 = const(25)
    LCDParamLine2 = const(35)
    LCDParamLine3 = const(45)
    LCDParamLine4 = const(55)
    LCDParamLine5 = const(65)

    LCDStatusLine1 = const(80)
    LCDStatusLine2 = const(90)
    LCDStatusLine3 = const(100)

    TestConfigFile = 'PCBA-32109Rev6'
    # TestConfigFile = 'PCBA-31334'
    # TestConfigFile = 'fastTest'
    # TestConfigFile = 'superFastTest'
    loadTestSettings(TestConfigFile)

    lcd_title_area()

    ON_TIME_ms, OFF_TIME_ms = format(PULSE_WIDTH_ms, DUTY_CYCLE, ON_TIME_ms, OFF_TIME_ms)

    killPower()  # remove power to make it safe to unload the pcbas
    # readI(5) #current measurement step

    # print (micropython.mem_info())
    performTest()

    keepPowerOn()
    # readI(5) #read current and leave power on
    killPower()  # remove power to make it safe to unload the pcbas
    machine.reset()
