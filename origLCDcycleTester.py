#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  4 17:13:49 2018
VERSION 1.0
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
    * Looks like other projects are using pins 12 and 13 for rotary encoders on ESP8266...
"""

import st7735, rgb, rgb_text #Display required imports
import utime, machine #Cycle count required imports
from micropython import const
import micropython
import gc
gc.enable()

# import importlib  #not available in micropython as of 2/4/2018. this will be a better way to import modules

utime.sleep_ms(500)
print("booting")

# -------------------------Hardware Config------------------------------#

print("configuring hardware")
DISPLAY_UPDATE_INTERVAL = const(56) #Do not set below 56 or the display will not update
TOGGLE_PIN_1 = const(4)
#TOGGLE_PIN_2 = const(11)

buttonPin = const(0)
ENCODER_PIN_1 = const(9)
ENCODER_PIN_2 = const(10)

RED = rgb.color565(255,0,0)
BLUE = rgb.color565(0,255,0)
GREEN = rgb.color565(0,0,255)
BLACK = rgb.color565(0,0,0)

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
# -----------------------------------------------------------#

# ---------------------------Setup--------------------------------#
print("performing Setup")
###togglePin = machine.Pin(TOGGLE_PIN_1, machine.Pin.OUT, machine.Pin.PULL_UP) #Pulls the LCD Reset(rst) pin high.
###button = machine.Pin(buttonPin, machine.Pin.IN, machine.Pin.PULL_UP)

# display = st7735.ST7735R(machine.SPI(1, baudrate=10000000),
#                          dc=machine.Pin(12),
#                          cs=machine.Pin(15),
#                          rst=machine.Pin(16))
#
# display.fill( rgb.color565(0,0,0) )

# -----------------------------------------------------------#

# -----------------------------------------------------------#
# def loadTestSettings(TestConfigFile):
#     global  TEST_NAME_1, TEST_NAME_2,\
#             NUMBER_OF_CYCLES,\
#             PULSE_WIDTH_ms, DUTY_CYCLE,\
#             ON_TIME_ms, OFF_TIME_ms,\
#             INVERTED
#
#     TestConfig = __import__(TestConfigFile)
#
#     TEST_NAME_1 = TestConfig.TEST_NAME_1
#     TEST_NAME_2 = TestConfig.TEST_NAME_2
#     NUMBER_OF_CYCLES = TestConfig.NUMBER_OF_CYCLES
#     PULSE_WIDTH_ms = TestConfig.PULSE_WIDTH_ms
#     DUTY_CYCLE = TestConfig.DUTY_CYCLE
#     ON_TIME_ms  = TestConfig.ON_TIME_ms
#     OFF_TIME_ms = TestConfig.OFF_TIME_ms
#     INVERTED = TestConfig.INVERTED

# def on_off_time_calc(PULSE_WIDTH_ms=1000, DUTY_CYCLE=50, ON_TIME_ms=250, OFF_TIME_ms=100):
#     '''This function properly configures the ON_TIME_ms and OFF_TIME_ms based on the configuration settings given '''
#     if PULSE_WIDTH_ms != 0:
#         ON_TIME_ms = int(PULSE_WIDTH_ms*(DUTY_CYCLE/100))
#         OFF_TIME_ms = int(PULSE_WIDTH_ms-ON_TIME_ms)
#     else:
#         ON_TIME_ms = int(ON_TIME_ms)
#         OFF_TIME_ms = int(OFF_TIME_ms)
#         PULSE_WIDTH_ms = int(ON_TIME_ms+OFF_TIME_ms)
#         DUTY_CYCLE = trunc(((ON_TIME_ms/PULSE_WIDTH_ms)*100),2)
#
#     time=( (ON_TIME_ms+OFF_TIME_ms)*NUMBER_OF_CYCLES )
#
#     printLCD("PW  = "+prettyTime(PULSE_WIDTH_ms), Y=LCDParamLine1 )
#     printLCD("DS  = "+str(DUTY_CYCLE)+"%", Y=LCDParamLine2 )
#     printLCD("ON  = "+prettyTime(ON_TIME_ms, 3), Y=LCDParamLine3 )
#     printLCD("OFF = "+prettyTime(OFF_TIME_ms, 3), Y=LCDParamLine4 )
#     printLCD("Time= "+prettyTime(time, 3), Y=LCDParamLine5 )
#
#     global enable, disable
#     if INVERTED == True:
#         enable  = togglePin.off
#         disable = togglePin.on
#     else:
#         enable  = togglePin.on
#         disable = togglePin.off
#
#     gc.collect()
#     return ( ON_TIME_ms, OFF_TIME_ms )

# def readI(seconds):
#     printLCD("Enabling DC power",Y=LCDStatusLine1)
#     enable()
#     printLCD("Dwell for "+ str(seconds) + " seconds",Y=LCDStatusLine2)
#     utime.sleep_ms(seconds*1000) #allow time for the readings to stabilize
#     printLCD("Take measurement now",Y=LCDStatusLine1, Background=0xaaaa)
#     printLCD("Press Button",Y=LCDStatusLine2, Background=0x0)
#     printLCD("",Y=LCDStatusLine3, Background=0x0)
#     while button.value() == 1:
#         utime.sleep_ms(50)
#     printLCD("", Y=LCDStatusLine1)
#     printLCD("", Y=LCDStatusLine2)
#     printLCD("", Y=LCDStatusLine3)
#     return
#
# def killPower():
#     disable()
#     printLCD("Power is off", Y=LCDStatusLine1)
#     printLCD("load/unload PCBA", Y=LCDStatusLine2)
#     printLCD("Press button", Y=LCDStatusLine3)
#     while button.value() == 1:
#         utime.sleep_ms(50)
#     printLCD("", Y=LCDStatusLine1)
#     printLCD("", Y=LCDStatusLine2)
#     printLCD("", Y=LCDStatusLine3)
#     return
#
# def keepPowerOn():
#     disable()
#     printLCD("Press button to", Y=LCDStatusLine2)
#     printLCD("turn power off", Y=LCDStatusLine3)
#     while button.value() == 1:
#         utime.sleep_ms(50)
#     printLCD("", Y=LCDStatusLine1)
#     printLCD("", Y=LCDStatusLine2)
#     printLCD("", Y=LCDStatusLine3)
#     return
#
# def cycle(ON_TIME_ms, OFF_TIME_ms):
#     enable()
#     utime.sleep_ms(ON_TIME_ms)
#     disable()
#     utime.sleep_ms(OFF_TIME_ms)
#     gc.collect()

# def printLCD(text, X=0, Y=0, Background=0x0000, Color=0xffff ):
#     text = str(text)
#     (rgb_text.text(display, text, x=X, y=Y, color=Color, background=Background))

# def truncate(num, digits=1):
#     '''Truncate a number to a specified number of decimal positions
#     num = int or float (kinda pointless for an int...)
#     digits = int (if a float is given, it is converted to an int.
#     Returns: float'''
#     digits=int(digits)
#     if digits>0:
#         mult=int(10**digits)
#         truncNum = int(num * mult) / float(mult)# left shift, chop, right shift
#     else:
#         truncNum = int(num)
#     return truncNum

# def prettyTime(milliseconds, msPrecision=1, verbose=False):
#     '''convert milliseconds to a pretty output.
#     If verbose is True, it will output days, hours, minutes, seconds, milliseconds
#     If verbose is False, it will display only the minimum values needed'''
#     seconds, milliseconds = divmod(milliseconds, 1000)
#     minutes, seconds = divmod(seconds, 60)
#     hours, minutes = divmod(minutes, 60)
#     days, hours = divmod(hours, 24)
#     weeks, days = divmod(days, 7)
#     years, weeks = divmod(weeks, 52)
#
#     time=str("%1dy %1dw %1dd" % (years, weeks, days))
#     if verbose == False:
#         if years == 0:
#             time=str("%1dw %1dd %1dh" % (weeks, days, hours))
#             if weeks == 0:
#                 time=str("%1dd %1dh %02dm" % (days, hours, minutes))
#                 if days == 0:
#                     time=str("%1dh %02dm %02ds" % (hours, minutes, seconds))
#                     if hours == 0:
#                         time=str("%02dm %02ds" % (minutes, seconds))
#                         if minutes == 0:
#                             time=str("%04.2fs" % (seconds+(milliseconds/1000)))
#                             if seconds == 0:
#                                 time=str("%1dms" % (truncate(milliseconds, digits=msPrecision)))
#     else:
#         time=str("%1dy %1dw %1dd %1dh %02dm %02ds.%3ds" % (years, weeks, days, hours, minutes, seconds, milliseconds))
#     return time

# def header():
#     display.fill_rectangle(0,0,128,18, rgb.color565(255,0,0) )
#     printLCD(TEST_NAME_1, Y=LCDTitle1, Background=BLUE)
#     printLCD(TEST_NAME_2, Y=LCDTitle2, Background=BLUE)
#
# def test_param():
#     display.fill_rectangle(20,0,128,70, rgb.color565(0,0,0) )
#     printLCD(TEST_NAME_1, Y=LCDTitle1, Background=BLACK)
#     printLCD(TEST_NAME_2, Y=LCDTitle2, Background=BLACK)
#
# def test_status():
#     display.fill_rectangle(0,0,128,18, rgb.color565(255,0,0) )
#     printLCD(TEST_NAME_1, Y=LCDTitle1, Background=BLUE)
#     printLCD(TEST_NAME_2, Y=LCDTitle2, Background=BLUE)

# def performTest():
#     updatesDisabled = False
#
#     def updateDisplay(count):
#         if updatesDisabled == True:
#             return
#         printLCD(str(count) + " of " + str(NUMBER_OF_CYCLES) ,Y=LCDStatusLine2)
#         rt=( (ON_TIME_ms + OFF_TIME_ms)*(NUMBER_OF_CYCLES-count) ) # rt stands for Remaining Time
#         rt=prettyTime(rt, verbose=False)
#         printLCD("Left:" + str(rt), Y=LCDStatusLine3 )
#
#     printLCD("Test in progress",Y=LCDStatusLine1)
#     if ON_TIME_ms < DISPLAY_UPDATE_INTERVAL and OFF_TIME_ms < DISPLAY_UPDATE_INTERVAL:
#         printLCD("Updates Disabled", Y=LCDStatusLine2)
#         printLCD("Cycles= "+ str(NUMBER_OF_CYCLES),Y=LCDStatusLine3)
#         updatesDisabled = True
#     else:
#         updateDisplay(NUMBER_OF_CYCLES)
#
#     displayUpdateDue=utime.ticks_add(utime.ticks_ms(), DISPLAY_UPDATE_INTERVAL)
#     displayUpdateRemaining = utime.ticks_diff(utime.ticks_ms(), displayUpdateDue)
#
#     for count in range(NUMBER_OF_CYCLES):
#         count+=1
#         waiting=True
#         deadline = utime.ticks_add(utime.ticks_ms(), +ON_TIME_ms)
#
#         enable()
#         while waiting == True:
#             msRemaining = utime.ticks_diff(utime.ticks_ms(), deadline)
#             if msRemaining <= -1: # the -1 is to allow for calculation time
#                 displayUpdateRemaining = utime.ticks_diff(utime.ticks_ms(), displayUpdateDue)
#                 if displayUpdateRemaining >= 0 and msRemaining <-55: # defer the update if there is not enough time before the next toggle state change
#                     updateDisplay(count)
#                     displayUpdateDue=utime.ticks_add(utime.ticks_ms(), DISPLAY_UPDATE_INTERVAL)
#             else:
#                 waiting = False
#
#         disable()
#         waiting = True
#         deadline = utime.ticks_add(utime.ticks_ms(), +OFF_TIME_ms)
#         while waiting == True:
#             msRemaining = utime.ticks_diff(utime.ticks_ms(), deadline)
#             if msRemaining <= -1: # the -1 is to allow for calculation time
#                 displayUpdateRemaining = utime.ticks_diff(utime.ticks_ms(), displayUpdateDue)
#                 if  displayUpdateRemaining >= 0 and msRemaining <-55: # defer the update if there is not enough time before the next toggle state change
#                     updateDisplay(count)
#                     displayUpdateDue=utime.ticks_add(utime.ticks_ms(), DISPLAY_UPDATE_INTERVAL)
#             else:
#                 waiting = False
#
#     updateDisplay(count)



# -----------------------------------------------------------#
gc.collect()

machine.freq(80000000)
#machine.freq(160000000)

TestConfigFile = 'PCBA-32109Rev6'
#TestConfigFile = 'PCBA-31334'
#TestConfigFile = 'fastTest'
#TestConfigFile = 'superFastTest'
loadTestSettings(TestConfigFile)

lcd_title_area()

ON_TIME_ms, OFF_TIME_ms  = format(PULSE_WIDTH_ms, DUTY_CYCLE, ON_TIME_ms, OFF_TIME_ms)

killPower() #remove power to make it safe to unload the pcbas
#readI(5) #current measurement step

#print (micropython.mem_info())
performTest()

keepPowerOn()
#readI(5) #read current and leave power on
killPower() #remove power to make it safe to unload the pcbas
machine.reset()








# my cheatsheet...
#display.fill( rgb.color565(255,255,0) )
#display.fill_rectangle(30,10,40,60, rgb.color565(0,0,255) )
#display.hline(100,100,20, rgb.color565(0,255,0) )

#rgb_text.text(display, "hello my name is", color=0xffff, background=0x1111)

#import micropython; micropython.mem_info()


