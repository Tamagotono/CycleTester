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

import st7735, rgb, rgb_text #Display required imports
import utime, machine #Cycle count required imports
from micropython import const
import micropython
import gc

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

    time:=str("%1dy %1dw %1dd" % (years, weeks, days))
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
                                time=str("%1dms" % (trunc(milliseconds, digits=msPrecision)))
    else:
        time=str("%1dy %1dw %1dd %1dh %02dm %02ds.%3ds" % (years, weeks, days, hours, minutes, seconds, milliseconds))
    return time

class GUI2LCD:
    """
    Args:

    Note:
        Used to convert generic display changes to LCD Driver commands.
        This should make it easier to adapt to various displays.
    """


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
    def __init__(self,
                 title_size: int = 1,
                 nav_size: int = 0,
                 parameter_size: int = 4,
                 status_size: int = 3,
                 notification_size: int = 1
                 ):

    def lcd_title_area():
        display.fill_rectangle(0, 0, 128, 18, rgb.color565(255, 0, 0))
        printLCD(TEST_NAME_1, Y=LCDTitle1, Background=BLUE)
        printLCD(TEST_NAME_2, Y=LCDTitle2, Background=BLUE)

    def lcd_param_area():
        display.fill_rectangle(20, 0, 128, 70, rgb.color565(0, 0, 0))
        printLCD(TEST_NAME_1, Y=LCDTitle1, Background=BLACK)
        printLCD(TEST_NAME_2, Y=LCDTitle2, Background=BLACK)

    def lcd_status_area():
        display.fill_rectangle(0, 0, 128, 18, rgb.color565(255, 0, 0))
        printLCD(TEST_NAME_1, Y=LCDTitle1, Background=BLUE)
        printLCD(TEST_NAME_2, Y=LCDTitle2, Background=BLUE)


class Test:
    """
    Args:

    Note:
        Defines the parameters of the test
    """
    pass

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
