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
DONE: Make a separate class to update the different panes of the display
    * Allow live adjustment of the settings
    * Allow saving of new profiles
    * Add an encoder for navigating the menus. (Soldered to pins 9 and 10)
    * Add Wifi interface for manual control or checking current status
    * Switch to the importlib method of loading variable modules, when this feature is added to uPy. (Not available)

NOTE:
    * For ESP8266, Using IO pin 2 for the toggle pin is a bad idea. It cycles multiple times during boot
    * Pin 4 seems to be tied to communications... Need to research for better choice of pins


"""

# import machine, display, time,
# import machine, _thread, math
# import m5stack
import utime, machine #Cycle count required imports
# from micropython import const
# import hardware_config
from hardware_config import M5stack
import gc

tft, btn_a, btn_b, btn_c = M5stack()  # Initialize the display and all 3 buttons

# ---------------------------------------------
# -------------GLOBAL VARIABLES----------------
# ---------------------------------------------

popupActive = False

# ---------------------------------------------


class UI:
    """
    Args:
        title_size (int): The number of lines for the Title pane. Default = 1
        nav_size (int): The number of lines for the Navigation pane. Set to 0 for test UIs. Default = 0
        parameter_size (int): The number of lines for the Parameter pane. Set to 0 for menu UIs. Default = 4
        status_size (int): The number of lines for the Status pane. Set to 0 for menu UIs. Default = 3
        notification_size (int): The number of lines for the Notification pane. Default = 1
    Note:
        This is the display for a specific test / menu. All calls to change the
    """
    global tft

    def __init__(self):
        tft.clear()

        self.screenwidth, self.screenheight = tft.screensize()

        self.header =     DisplayPane(0, 0, 40, self.screenwidth,
                                      text_color=tft.BLACK,
                                      font=tft.FONT_DejaVu18,
                                      fill_color=tft.BLUE,
                                      frame_color=tft.BLUE)

        self.parameters = DisplayPane(0, 40, 120, self.screenwidth,
                                      text_color=tft.YELLOW,
                                      fill_color=tft.BLACK,
                                      frame_color=tft.BLACK,
                                      font=tft.FONT_Default)

        self.status =     DisplayPane(0, 160, 58, self.screenwidth,
                                      text_color=tft.YELLOW,
                                      fill_color=tft.DARKGREY,
                                      frame_color=tft.DARKGREY)

        self.popup =      DisplayPane(30, 20, 203, 300,
                                      frame_color = tft.WHITE,
                                      fill_color = tft.BLUE,
                                      text_color = tft.WHITE,
                                      font = tft.FONT_DejaVu24,
                                      is_popup=True,
                                      corner_radius=0,
                                      func = self.refresh_all
                                      )

        self.panes = [self.header, self.parameters, self.status]

        self.footer()

        # self.__displaytest()
        print("test_UI instance created")
        # utime.sleep(10)
        # tft.clear()
        # self.popup.pop_up(220, 180)
        # utime.sleep(10)
        self.popup.pop_down()

    def __displaytest(self):
        """
        FOR TESTING PURPOSES ONLY
        WILL BE REMOVED BEFORE V1 RELEASE
        """

        i = 1
        while i <= self.header.num_of_lines:
            self.header.lines[i] = str(3.14159 * i)
            i += 1
        self.header.update_all_lines()

        i = 1
        while i <= self.parameters.num_of_lines:
            self.parameters.lines[i] = str(3.14159 * i)
            i += 1
        self.parameters.update_all_lines()

        i = 1
        while i <= self.status.num_of_lines:
            self.status.lines[i] = str(3.14159 * i)
            i += 1
        self.status.update_all_lines()


    def footer(self):
        """
        Returns:
            Nothing
        Notes:
            Draws the button labels at the bottom of the display, then sets the window to not include the footer area.
        """
        tft.font(tft.FONT_Ubuntu)
        tft.rect(  0, 220, self.screenwidth, 30, tft.YELLOW, tft.YELLOW)

        tft.rect( 25, 220, 80, 30, tft.BLUE, tft.BLUE)
        tft.text( 50, 222,   "UP", tft.WHITE, transparent=True)

        tft.rect(120, 220, 80, 30, tft.BLUE, tft.BLUE)
        tft.text(125, 222, "DOWN", tft.WHITE, transparent=True)

        tft.rect(215, 220, 80, 30, tft.BLUE, tft.BLUE)
        tft.text(230, 222,  "SEL", tft.WHITE, transparent=True)

    def refresh_all(self):
        """
        Returns:
            Nothing
        Notes:
            Gets passed as a callback, to allow all panes to be redrawn, but called from the is_popup pane.
        """
        for pane in self.panes:
            pane.update_all_lines()
        self.footer()

class DisplayPane:
    def __init__(self,
                 x:int,
                 y:int,
                 frame_height:int,
                 frame_width:int,
                 frame_color:int = tft.WHITE,
                 fill_color:int = tft.BLUE,
                 text_color:int = tft.WHITE,
                 font = tft.FONT_DejaVu18,
                 is_popup = False,
                 corner_radius = 0,
                 func = None
                 ):

        self.x = x
        self.y = y
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frame_color = frame_color
        self.fill_color = fill_color
        self.text_color = text_color
        self.font = font
        self.is_popup = is_popup
        self.corner_radius = corner_radius
        tft.font(self.font)
        self.func = func
        self.line_height, self.text_y = self.line_height_margin_calc(10)
        self.num_of_lines = int(self.frame_height / self.line_height)
        # print(str(self.font))
        # print("self.x = " + str(self.x))
        # print("self.y = " + str(self.y))
        # print("self.frameheight = " + str(self.frame_height))
        # print("lineheight =" + str(self.line_height))
        # print("num of lines = " + str(self.num_of_lines))
        self.lines = {}

        tft.set_bg(self.fill_color)
        tft.set_fg(self.text_color)

        self.__create_lines(self.num_of_lines)
        self.__initialize_pane()

    def __initialize_pane(self):
        self.__initialize_pane_frame()
        self.__initialize_pane_text()

    def __initialize_pane_frame(self):
        tft.roundrect(self.x, self.y, self.frame_width, self.frame_height, self.corner_radius,
                      self.frame_color, self.fill_color)

    def __initialize_pane_text(self):
        tft.font(self.font)
        self.__create_lines(self.num_of_lines)
        self.update_all_lines()

    def line_height_margin_calc(self, margin:int=10) -> Tuple(int, int):
        """
        Args:
            margin_pct (int): the percentage of font size for vertical margins
        Returns:
            The total hight of the line in pixels
            The number of pixels used above the font used for margins, to set the vertical offset for text_y
        """
        margin_pct = margin/100
        font_height = int(tft.fontSize()[1])
        margin_px = int(font_height)
        line_height_px = int(font_height * (1 + margin_pct))
#        print("line_height_margin_calc: line_height_px = " + str(line_height_px) + 'margin:' + str(margin/2))
        return line_height_px, int(margin_px/4)

    def __create_lines(self, num_of_lines:int):
        """
        Args:
            num_of_lines (int): initializes the dictionary of the text for each line number
        Returns:
            Nothing
        """
        line_num = 1
        while line_num <= num_of_lines:
            self.lines[line_num] = str('')
            line_num += 1
#        print(self.lines.items())

    def update_line(self, line_number:int):
        """
        Args:
            line_number (int): The line number to update on the display
        Returns:
            Nothing
        Notes:
            Does nothing if popupActive == True and the instance is not set as a popup via the is_popup variable.
        """
        global popupActive

        if popupActive == True == self.is_popup:
            return
        else:
            tft.font(self.font)
            line_y = (((line_number - 1) * self.line_height) + self.y)
            text_y = line_y + self.text_y
            self.__initialize_pane_frame()
            tft.text(self.x, text_y, self.lines.get(line_number, "ERROR"), self.text_color, transparent=True)

    def update_all_lines(self):
        """
        Returns:
            Nothing
        Notes:
            Quick way to update all lines in the pane
        """
        self.__initialize_pane_frame()
        line_num = 1
        while line_num <= self.num_of_lines:
            self.update_line(line_num)
            line_num += 1

    def pop_up(self, popup_width:int=260, popup_height: int=200):
        global popupActive
        popupActive = True
        tft.clearwin(tft.YELLOW)

        x, y = tft.screensize()

        if self.frame_height == -1:
            self.frame_height = popup_height

        if self.frame_width == -1:
            self.frame_width = popup_width

        x_offset = int((x - self.frame_width) / 2)
        y_offset = int((y - self.frame_height) / 2)

        self.x = x_offset
        self.y = y_offset

        self.__initialize_pane()


    def pop_down(self):
        global popupActive
        popupActive = False
        tft.clearwin()
        self.func()  # callback function to redraw all panes

    # def printLCD(text, X=0, Y=0, bg_color=0x000000, text_color=0xffffff, transparent=True):
    #     text = str(text)
    #     tft.textClear(X, Y, text)
    #     tft.text(X, Y, text, text_color, transparent=True)
    #

#
# class Test:
#     """
#     Args:
#
#     Note:
#         Defines the parameters of the test
#     """
#     def __init__(self, on_time_ms: int, off_time_ms: int, relay: Relay, button: machine.Signal, display ):
#         pass
#
#     def read_current(seconds: int, relay: Relay) -> None:
#         printLCD("Enabling DC power", Y=LCDStatusLine1)
#         relay.on()
#         printLCD("Dwell for " + str(seconds) + " seconds", Y=LCDStatusLine2)
#         utime.sleep_ms(seconds * 1000)  # allow time for the readings to stabilize
#         printLCD("Take measurement now", Y=LCDStatusLine1, Background=0xaaaa)
#         printLCD("Press Button", Y=LCDStatusLine2, Background=0x0)
#         printLCD("", Y=LCDStatusLine3, Background=0x0)
#         while button.value() == 1:
#             utime.sleep_ms(50)
#         printLCD("", Y=LCDStatusLine1)
#         printLCD("", Y=LCDStatusLine2)
#         printLCD("", Y=LCDStatusLine3)
#         return
#
#     def kill_power():
#         disable()
#         printLCD("Power is off", Y=LCDStatusLine1)
#         printLCD("load/unload PCBA", Y=LCDStatusLine2)
#         printLCD("Press button", Y=LCDStatusLine3)
#         while button.value() == 1:
#             utime.sleep_ms(50)
#         printLCD("", Y=LCDStatusLine1)
#         printLCD("", Y=LCDStatusLine2)
#         printLCD("", Y=LCDStatusLine3)
#         return
#
#     def keep_power_on():
#         disable()
#         printLCD("Press button to", Y=LCDStatusLine2)
#         printLCD("turn power off", Y=LCDStatusLine3)
#         while button.value() == 1:
#             utime.sleep_ms(50)
#         printLCD("", Y=LCDStatusLine1)
#         printLCD("", Y=LCDStatusLine2)
#         printLCD("", Y=LCDStatusLine3)
#         return
#
#     def perform_test():
#         updatesDisabled = False
#
#         def updateDisplay(count):
#             if updatesDisabled == True:
#                 return
#             printLCD(str(count) + " of " + str(NUMBER_OF_CYCLES), Y=LCDStatusLine2)
#             rt = ((ON_TIME_ms + OFF_TIME_ms) * (NUMBER_OF_CYCLES - count))  # rt stands for Remaining Time
#             rt = prettyTime(rt, verbose=False)
#             printLCD("Left:" + str(rt), Y=LCDStatusLine3)
#
#         printLCD("Test in progress", Y=LCDStatusLine1)
#         if ON_TIME_ms < DISPLAY_UPDATE_INTERVAL and OFF_TIME_ms < DISPLAY_UPDATE_INTERVAL:
#             printLCD("Updates Disabled", Y=LCDStatusLine2)
#             printLCD("Cycles= " + str(NUMBER_OF_CYCLES), Y=LCDStatusLine3)
#             updatesDisabled = True
#         else:
#             updateDisplay(NUMBER_OF_CYCLES)
#
#         displayUpdateDue = utime.ticks_add(utime.ticks_ms(), DISPLAY_UPDATE_INTERVAL)
#         displayUpdateRemaining = utime.ticks_diff(utime.ticks_ms(), displayUpdateDue)
#
#         for count in range(NUMBER_OF_CYCLES):
#             count += 1
#             waiting = True
#             deadline = utime.ticks_add(utime.ticks_ms(), +ON_TIME_ms)
#
#             enable()
#             while waiting == True:
#                 msRemaining = utime.ticks_diff(utime.ticks_ms(), deadline)
#                 if msRemaining <= -1:  # the -1 is to allow for calculation time
#                     displayUpdateRemaining = utime.ticks_diff(utime.ticks_ms(), displayUpdateDue)
#                     if displayUpdateRemaining >= 0 and msRemaining < -55:  # defer the update if there is not enough time before the next toggle state change
#                         updateDisplay(count)
#                         displayUpdateDue = utime.ticks_add(utime.ticks_ms(), DISPLAY_UPDATE_INTERVAL)
#                 else:
#                     waiting = False
#
#             disable()
#             waiting = True
#             deadline = utime.ticks_add(utime.ticks_ms(), +OFF_TIME_ms)
#             while waiting == True:
#                 msRemaining = utime.ticks_diff(utime.ticks_ms(), deadline)
#                 if msRemaining <= -1:  # the -1 is to allow for calculation time
#                     displayUpdateRemaining = utime.ticks_diff(utime.ticks_ms(), displayUpdateDue)
#                     if displayUpdateRemaining >= 0 and msRemaining < -55:  # defer the update if there is not enough time before the next toggle state change
#                         updateDisplay(count)
#                         displayUpdateDue = utime.ticks_add(utime.ticks_ms(), DISPLAY_UPDATE_INTERVAL)
#                 else:
#                     waiting = False
#
#         updateDisplay(count)

class Relay(machine.Signal):
    """
    Notes:
        Adds extra feature to the machine.Signal class

    Adds:
        toggle: Inverts the current state of the pin.
    """
    def __init__(self, gpio_pin_number: int, inverted=False):
        super().__init__(gpio_pin_number, inverted)

    # def on(self):
    #     print("click")
    #     self.on()
    #
    # def off(self):
    #     print("clack")
    #     self.off()

    def toggle(self):
        print("clickk")
        self.value(not self.value())


class Button:
    def __init__(self, gpio_pin_number: int):
        self.gpio_pin = machine.Pin(gpio_pin_number, machine.Pin.IN, machine.Pin.PULL_UP)
    pass

class Encoder:
    def __init__(self):
        pass

class Test:
    total_time = 0
    def __init__(self,
                 relay: Relay,
                 cycles: int,
                 on_time: int=0,
                 off_time: int=0,
                 pulse_width_ms: int=0,
                 duty_cycle: float=0,
                 periodic_function = None,
                 func_param = None,
                 func_call_freq: int=0):

        self.on_time = on_time
        self.off_time = off_time
        self.pulse_width_ms = pulse_width_ms
        self.duty_cycle = duty_cycle
        self.cycles = cycles
        self.relay = relay
        self.periodic_function = periodic_function
        self.func_call_freq = func_call_freq
        self.func_param = func_param
        if self.periodic_function is None:
            self.periodic_function = self.__pass

        self.ontime, self.offtime, self.pulse_width_ms, self.duty_cycle = on_off_time_calc(on_time,
                                                                                           off_time,
                                                                                           pulse_width_ms,
                                                                                           duty_cycle)


    def begin_test(self):
        gc.collect()

        cycle_num = 0
        while cycle_num < self.cycles:
            if self.func_call_freq > 0 and cycle_num % self.func_call_freq == 0:
                self.periodic_function(self.func_param)
            cycle(self.on_time, self.off_time, self.relay)
            print("begin test  " + __name__ + str(cycle_num))
            from tests.TEST_32109 import test_UI
            test_UI.status.lines[1] = "Cycle %d of %d" % (cycle_num, self.cycles)
            test_UI.status.update_line(1)
            cycle_num += 1

    def __pass(self):
        """
        Returns:
            Nothing
        Notes:
            Dummy module for use with Test class, in case a func_call_freq is assigned but no function passed.
        """
        pass

# def prettyTime(milliseconds: int, msPrecision: int=1, verbose: bool=False) -> str:
#     """
#     Args:
#         milliseconds: The value in milliseconds to on_off_time_calc
#         msPrecision: The number of digits to show for the milliseconds portion of the output.
#                      Default = 1
#         verbose: If verbose is True, it will output days, hours, minutes, seconds, milliseconds.
#                  If verbose is False, it will display only the minimum values needed.
#                  Default = False
#
#     Returns: A string with the converted time in human readable on_off_time_calc with the precision specified.
#     """
#     seconds, milliseconds = divmod(milliseconds, 1000)
#     minutes, seconds = divmod(seconds, 60)
#     hours, minutes = divmod(minutes, 60)
#     days, hours = divmod(hours, 24)
#     weeks, days = divmod(days, 7)
#     years, weeks = divmod(weeks, 52)
#
#     time = str("%1dy %1dw %1dd" % (years, weeks, days))
#     if verbose == False:
#         if years == 0:
#             time = str("%1dw %1dd %1dh" % (weeks, days, hours))
#             if weeks == 0:
#                 time=str("%1dd %1dh %02dm" % (days, hours, minutes))
#                 if days == 0:
#                     time=str("%1dh %02dm %02ds" % (hours, minutes, seconds))
#                     if hours == 0:
#                         time=str("%02dm %02ds" % (minutes, seconds))
#                         if minutes == 0:
#                             time=str("%04.2fs" % (seconds+(milliseconds/1000)))
#                             if seconds == 0:
#                                 time=str("%sms" % truncate(milliseconds, precision=msPrecision))
#     else:
#         time=str("%1dy %1dw %1dd %1dh %02dm %02d.%3ds" % (years, weeks, days, hours, minutes, seconds, milliseconds))
#     return time

def prettyTime(milliseconds: int, msPrecision: int=1, verbose: bool=False) -> str:
    """
    Args:
        milliseconds: The value in milliseconds to on_off_time_calc
        msPrecision: The number of digits to show for the milliseconds portion of the output.
                     Default = 1
        verbose: If verbose is True, it will output days, hours, minutes, seconds, milliseconds.
                 If verbose is False, it will display only the minimum values needed.
                 Default = False

                 If a negative value is entered, it is set to 0

    Returns: A string with the converted time in human readable on_off_time_calc with the precision specified.
    """
    years = weeks = days = hours = minutes = 0

    if milliseconds < 0:
        milliseconds = 0  # No negatives for you ...

    if verbose == False:

        if milliseconds < 1000:
            time = str("%sms" % truncate(milliseconds, precision=msPrecision))
        elif milliseconds < 60000:  # less than 1 minute
            time = str("%04.2fs" % (milliseconds / 1000))
        elif milliseconds < 3600000:  # less than 1 hour
            minutes, seconds = divmod(milliseconds, 60000)
            seconds = int(seconds/1000)
            time = str("%02dm %02ds" % (minutes, seconds))
        elif milliseconds < 86400000:  # less than 24 hours
            minutes, seconds = divmod(milliseconds, 60000)
            seconds = int(seconds / 1000)
            hours, minutes = divmod(minutes, 60)
            time = str("%1dh %02dm %02ds" % (hours, minutes, seconds))
        elif milliseconds < 604800000:  # less than 7 days
            hours, minutes = divmod(milliseconds, 3600000)
            minutes = int(minutes/60000)
            days, hours = divmod(hours, 24)
            time = str("%1dd %1dh %02dm" % (days, hours, minutes))
        elif milliseconds < 31449600000:  # less than 1 year
            days, hours = divmod(milliseconds, 86400000)
            hours = int(hours/3600000)
            weeks, days = divmod(days, 7)
            time = str("%1dw %1dd %1dh" % (weeks, days, hours))
        elif milliseconds > 31449600000:  # over 1 year
            weeks, days = divmod(milliseconds, 604800000)
            days = int(days/86400000)
            years, weeks = divmod(weeks, 52)
            time = str("%1dy %1dw %1dd" % (years, weeks, days))

    else:
        seconds, milliseconds = divmod(milliseconds, 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        weeks, days = divmod(days, 7)
        years, weeks = divmod(weeks, 52)

        time=str("%1dy %1dw %1dd %1dh %02dm %02d.%3ds" % (years, weeks, days, hours, minutes, seconds, milliseconds))
    return time


def truncate(original_number: float, precision: int=1) -> str:
    """
    Args:
        original_number: The float that you want truncated (not rounded)
        precision: Int defining how many decimal places to truncate at.

    Returns: The string of the original float, but truncated to the specified number of decimal places.
             Default = 1

    Notes: This has to return a string due to the accuracy in the MCU causing numbers to have too many digits.
    """
    precision=int(precision)
    if precision>0:
        temp = str(float(original_number)).split('.')  # float to force a decimal point, string to split.
        temp[1] = temp[1]+('0'*precision)  # make sure we have enough digits for the next step.
        truncated_number = temp[0]+'.'+temp[1][:precision]
    else:
        truncated_number = str(int(original_number))
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

# --------------- in work ----------
def on_off_time_calc(on_time_ms: int=250, off_time_ms: int=100, pulse_width_ms: int=1000, duty_cycle: float=50,):
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
        duty_cycle = float(truncate(((on_time_ms / pulse_width_ms) * 100), 2))

    gc.collect()
    return on_time_ms, off_time_ms, pulse_width_ms, duty_cycle

def update_parameters_pane():

    # print("on_time= %d, off_time= %d" % (on_time_ms, off_time_ms))
    test_window.parameters.lines[1] = ("PW   = %s"   % prettyTime(pulse_width_ms))
    test_window.parameters.lines[2] = ("DS   = %s%%" % str(duty_cycle))
    test_window.parameters.lines[3] = ("ON   = %s"   % prettyTime(on_time_ms, 1))
    test_window.parameters.lines[4] = ("OFF  = %s"   % prettyTime(off_time_ms, 1))
    test_window.parameters.lines[5] = ("Time = %s"   % prettyTime(time, 1))
    time = ((on_time_ms + off_time_ms) * NUMBER_OF_CYCLES)

def importlib(module_name: str, submodule_name: str=None):
    """
    Args:
        module_name (str): Name of module to import
        submodule_name (str): Name of the submodule to import [optional]
    Returns:
        the (sub)module
    Notes:
        You can import a submodule by
        i.e.  "getcwd = importlib('os', 'getcwd')"  is the same of "from os import getcwd"

        You can also use variables...
        i.e.  variable_module_name = 'os'
              cwd_is = importlib(variable_module_name, getcwd)" is the same as "from os import getcwd as cwd_is"
    """
    if submodule_name is None:
        return __import__(module_name)
    else:
        return __import__(module_name).__getattribute__(submodule_name)

#

# def load_test_settings(TestConfigFile):
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
#
# def m5():
#     a = m5stack.ButtonA(callback=button_hander_a)
#     b = m5stack.ButtonB(callback=button_hander_b)
#     c = m5stack.ButtonC(callback=button_hander_c)

if __name__ == "LCDcycleTest":
    gc.enable()
    gc.collect()

    #test_module = PCBA32109-TEST.py


    print("configuring hardware")
    test_window = UI()

    #on_off_time_calc()
    #test_window.parameters.update_all_lines()

    #DISPLAY_UPDATE_INTERVAL = const(56)  # Do not set below 56 or the display will not update
    #TOGGLE_PIN_1 = const(4)
    # TOGGLE_PIN_2 = const(11)
    #
    # buttonPin = const(0)
    # ENCODER_PIN_1 = const(9)
    # ENCODER_PIN_2 = const(10)


    # LCDTitle1 = const(0)
    # LCDTitle2 = const(10)
    #
    # LCDStatusLine1 = const(80)
    # LCDStatusLine2 = const(90)
    # LCDStatusLine3 = const(100)

    #TestConfigFile = 'PCBA-32109Rev6'
    # TestConfigFile = 'PCBA-31334'
    # TestConfigFile = 'fastTest'
    # TestConfigFile = 'superFastTest'
    # loadTestSettings(TestConfigFile)
    #
    # lcd_title_area()

    #ON_TIME_ms, OFF_TIME_ms = on_off_time_calc(PULSE_WIDTH_ms, DUTY_CYCLE, ON_TIME_ms, OFF_TIME_ms)

    # killPower()  # remove power to make it safe to unload the pcbas
    # # readI(5) #current measurement step
    #
    # # print (micropython.mem_info())
    # performTest()
    #
    # keepPowerOn()
    # # readI(5) #read current and leave power on
    # killPower()  # remove power to make it safe to unload the pcbas
    # machine.reset()
