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
import utime, machine  # Cycle count required imports
# from micropython import const
# import hardware_config
from hardware_config import M5stack
import lib.m5stack as m5stack
import gc
import uos as os

print("My __name__ is " + __name__)

tft, btn_a, btn_b, btn_c = M5stack()  # Initialize the display and all 3 buttons

# ---------------------------------------------
# -------------GLOBAL VARIABLES----------------
# ---------------------------------------------

popupActive = False

# ---------------------------------------------
def null():
    pass


class TestUI:
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

        self.popup =      DisplayPane(30, 20, 203, 300,
                                      frame_color=tft.WHITE,
                                      fill_color=tft.BLUE,
                                      text_color=tft.WHITE,
                                      font=tft.FONT_DejaVu24,
                                      is_popup=True,
                                      corner_radius=0,
                                      func=self.refresh_all
                                      )

        self.header =     DisplayPane(0, 0, 40, self.screenwidth,
                                      text_color=tft.WHITE,
                                      font=tft.FONT_DejaVu18,
                                      fill_color=tft.BLUE,
                                      frame_color=tft.BLUE
                                      )

        self.parameters = DisplayPane(0, 40, 90, self.screenwidth,
                                      text_color=tft.BLUE,
                                      fill_color=tft.WHITE,
                                      frame_color=tft.WHITE,
                                      font=tft.FONT_Ubuntu
                                      )

        self.status =     DisplayPane(0, 130, 88, self.screenwidth,
                                      text_color=tft.YELLOW,
                                      fill_color=tft.BLACK,
                                      frame_color=tft.BLACK,
                                      font=tft.FONT_DejaVu18
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
        tft.text( 50, 222, "UP", tft.WHITE, transparent=True)

        tft.rect(120, 220, 80, 30, tft.BLUE, tft.BLUE)
        tft.text(125, 222, "DOWN", tft.WHITE, transparent=True)

        tft.rect(215, 220, 80, 30, tft.BLUE, tft.BLUE)
        tft.text(230, 222, "SEL", tft.WHITE, transparent=True)

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

class MenuUI(TestUI):
    def __init__(self):

        tft.clear()

        self.screenwidth, self.screenheight = tft.screensize()

        self.header = Menu(x=0, y=0,
                           frame_height=40,
                           frame_width=self.screenwidth,
                           frame_color=tft.RED,
                           fill_color=tft.BLUE,
                           text_color=tft.WHITE,
                           font=tft.FONT_Comic,
                           is_popup=False,
                           corner_radius=0,
                           func=self.refresh_all
                           )

        self.menu = Menu(x=0, y=40,
                         frame_height=200,
                         frame_width=self.screenwidth,
                         frame_color=tft.RED,
                         fill_color=tft.BLUE,
                         text_color=tft.WHITE,
                         font=tft.FONT_DejaVu18,
                         is_popup=False,
                         corner_radius=0,
                         func=self.refresh_all
                         )

        self.footer()
        self.header.lines[1] = "Select Test"
        self.header.update_all_lines()

        # self.__displaytest()
        print("menu_UI instance created")
        # utime.sleep(10)
        # tft.clear()
        # self.popup.pop_up(220, 180)
        # utime.sleep(10)
        # self.popup.pop_down()
        pass


class DisplayPane:
    def __init__(self,
                 x: int,
                 y: int,
                 frame_height: int,
                 frame_width: int,
                 frame_color: int=tft.WHITE,
                 fill_color: int=tft.BLUE,
                 text_color: int=tft.WHITE,
                 font=tft.FONT_DejaVu18,
                 is_popup=False,
                 corner_radius=0,
                 func=None
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

        if self.is_popup is True:
            self.__initialize_pane_text()
        else:
            self.__initialize_pane()

    def __initialize_pane(self):
        self.__initialize_pane_frame()
        self.__initialize_pane_text()

    def __initialize_pane_frame(self):
        tft.set_bg(self.fill_color)
        tft.roundrect(self.x, self.y, self.frame_width, self.frame_height, self.corner_radius,
                      self.frame_color, self.fill_color)

    def __initialize_pane_line(self, y):
        tft.set_bg(self.fill_color)
        tft.roundrect(0, y, self.frame_width, self.line_height, 0,
                      self.frame_color, self.fill_color)

    def __initialize_pane_text(self):
        tft.font(self.font)
        self.__create_lines(self.num_of_lines)
        self.update_all_lines()

    def line_height_margin_calc(self, margin: int=10) -> Tuple(int, int):
        """
        Args:
            margin (int): the percentage of font size for vertical margins
        Returns:
            The total height of the line in pixels
            The number of pixels used above the font used for margins, to set the vertical offset for text_y
        """
        margin_pct = margin/100
        font_height = int(tft.fontSize()[1])
        margin_px = int(font_height)
        line_height_px = int(font_height * (1 + margin_pct))
#        print("line_height_margin_calc: line_height_px = " + str(line_height_px) + 'margin:' + str(margin/2))
        return line_height_px, int(margin_px/4)

    def __create_lines(self, num_of_lines: int):
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

    def update_line(self, line_number: int, font=None):
        """
        Args:
            line_number (int): The line number to update on the display
        Returns:
            Nothing
        Notes:
            Does nothing if popupActive == True and the instance is not set as a popup via the is_popup variable.
        """
        global popupActive

        if popupActive is True is not self.is_popup:
            return

        if font is not None:
            tft.font(font)
        else:
            tft.font(self.font)

        line_y = (((line_number - 1) * self.line_height) + self.y)
        text_y = line_y + self.text_y
        self.__initialize_pane_line(line_y)
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

    def pop_up(self, popup_width: int=260, popup_height: int=200):
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

        self.__initialize_pane_frame()
        self.update_all_lines()

    def pop_down(self):
        global popupActive
        popupActive = False
        tft.clearwin()
        self.func()  # callback function to redraw all panes


class Menu(DisplayPane):
    global tft

    def __init__(self, x: int, y: int, frame_height: int, frame_width: int,
                 frame_color: int=tft.WHITE, fill_color: int=tft.BLUE,
                 text_color: int=tft.WHITE, font=tft.FONT_DejaVu18,
                 is_popup=False,
                 corner_radius=0,
                 func=null):

        super().__init__(x, y, frame_height, frame_width, frame_color, fill_color, text_color, font,
                         is_popup, corner_radius, func)
        self.mount_sd()
        self.test_names_dict = self.get_test_names()
        self.test_names_list = [name for name in self.test_names_dict]
        self.test_names_list.sort()
        self.aperture_size = self.num_of_lines-2
        self.num_of_files = len(self.test_names_list)
        self.offset = 0
        self.highlighted = 0

        self.update_displayed_files()

    def move(self, direction: str):
        if 0 < self.offset > self.aperture_size:
                self.highlight(direction)
        else:
            self.scroll(direction)
            self.highlight()

    def highlight(self, direction: str = ""):
        self.update_line(self.highlighted)  # finally update the previous line that was highlighted then reset

        if direction == "up":
            line_num = self.highlighted + 1
        elif direction == "down":
            line_num = self.highlighted - 1
        else:
            line_num = self.highlighted
        
        self.highlighted = line_num
        self.lines[line_num] = ("=> " + str(self.lines[line_num]))
        self.update_line(line_num)
        self.lines[line_num] = self.lines[line_num][2:]  # reset currently highlighted line back to normal but don't update the display

    def scroll(self, direction: str):
        if direction == "up" and self.offset > 0:
            self.offset -= 1
        elif direction == "down" and (self.num_of_files - self.offset) > self.aperture_size:
            self.offset += 1

        self.lines[0:self.aperture_size] = self.test_names_list[self.offset:(self.offset + self.aperture_size)]
        self.update_all_lines()

    def mount_sd(self):
        m5stack.sdconfig()
        try:
            os.mountsd()
        except:
            print("NO SD CARD")
        utime.sleep_ms(100)

    def update_displayed_files(self):
        max_displayed_files = self.num_of_lines - 2  # reserving top 2 lines for header
        files_alpha = []
        files_alpha = [filename for filename in self.get_test_names()]
        files_alpha.sort()
        print(files_alpha)
        offset = 0

        self.lines[1] = files_alpha[offset]
        self.lines[2] = files_alpha[offset+1]
        self.lines[3] = files_alpha[offset+2]
        self.lines[4] = files_alpha[offset+3]
        self.lines[5] = files_alpha[offset+4]

        self.update_all_lines()
        pass

    def get_test_names(self):
        files = []
        test_files = {}
        try:
            files = os.listdir('/sd')
        except:
            self.mount_sd()
            print("No SD Card Mounted ... now mounting...")

        for filename in files:
            if filename[:5] == "TEST_" and filename[-3:].lower() == ".py":
                test_files[filename[5:-3]] = filename

        print(test_files.items())
        return test_files

class Relay(machine.Signal):
    """
    Notes:
        Adds extra feature to the machine.Signal class

    Adds:
        toggle: Inverts the current state of the pin.
    """
    def __init__(self, gpio_pin_number: Pin, inverted=False):
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
                 periodic_function=None,
                 func_param=None,
                 func_call_freq: int=0):

        # self.on_time = on_time
        # self.off_time = off_time
        # self.pulse_width_ms = pulse_width_ms
        # self.duty_cycle = duty_cycle
        self.cycles = cycles
        self.relay = relay
        self.periodic_function = periodic_function
        self.func_call_freq = func_call_freq
        self.func_param = func_param
        if self.periodic_function is None:
            self.periodic_function = self.__pass

        self.on_time, self.off_time, self.pulse_width_ms, self.duty_cycle = on_off_time_calc(on_time,
                                                                                             off_time,
                                                                                             pulse_width_ms,
                                                                                             duty_cycle)

    def __str__(self):
        return self.on_time, self.off_time, self.pulse_width_ms, self.duty_cycle, self.cycles

    def __getitem__(self, item):
        items = (self.on_time, self.off_time, self.pulse_width_ms, self.duty_cycle, self.cycles)
        return items[item]

    def begin_test(self):
        gc.collect()

        test_UI.status.lines[1] = "Cycle   of"
        test_UI.status.update_line(1)

        cycle_num = 1
        while cycle_num <= self.cycles:
            if self.func_call_freq > 0 and cycle_num % self.func_call_freq == 0:
                self.periodic_function(self.func_param)
            cycle(self.on_time, self.off_time, self.relay)
            test_UI.status.lines[3] = " %d  :  %d" % (cycle_num, self.cycles)
            test_UI.status.update_line(3, tft.FONT_7seg)
            cycle_num += 1
        test_UI.status.lines[1] = "Completed %d cycles" % self.cycles
        test_UI.status.update_line(1)

        test_UI.popup.lines[1] = "TEST COMPLETE"
        test_UI.popup.lines[2] = "%d Cycles" % self.cycles
        test_UI.popup.lines[4] = "You may now "
        test_UI.popup.lines[5] = "Remove the "
        test_UI.popup.lines[6] = "board(s)"
        test_UI.popup.pop_up()
        # utime.sleep(10)
        # test_UI.popup.pop_down()

    def __pass(self):
        """
        Returns:
            Nothing
        Notes:
            Dummy module for use with Test class, in case a func_call_freq is assigned but no function passed.
        """
        pass

class SD:
    def __init__(self):
        m5stack.sdconfig()


def pretty_time(milliseconds: int, precision_ms: int=1, verbose: bool=False) -> str:
    """
    Args:
        milliseconds: The value in milliseconds to on_off_time_calc
        precision_ms: The number of digits to show for the milliseconds portion of the output.
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

    if not verbose:

        if milliseconds < 1000:
            time = str("%sms" % truncate(milliseconds, precision=precision_ms))
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

        time = str("%1dy %1dw %1dd %1dh %02dm %02d.%3ds" % (years, weeks, days, hours, minutes, seconds, milliseconds))
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
    precision = int(precision)
    if precision > 0:
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

def on_off_time_calc(on_time_ms: int=0, off_time_ms: int=0, pulse_width_ms: int=0, duty_cycle: float=0,):
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
        print("pulse width = " + str(pulse_width_ms))
        on_time_ms = int(pulse_width_ms * (duty_cycle / 100))
        off_time_ms = int(pulse_width_ms - on_time_ms)
        print((on_time_ms, off_time_ms, pulse_width_ms, duty_cycle))
    else:
        print("on time = " + str(pulse_width_ms))
        on_time_ms = int(on_time_ms)
        off_time_ms = int(off_time_ms)
        pulse_width_ms = int(on_time_ms + off_time_ms)
        duty_cycle = float(truncate(((on_time_ms / pulse_width_ms) * 100), 2))
        print((on_time_ms, off_time_ms, pulse_width_ms, duty_cycle))

    gc.collect()
    return on_time_ms, off_time_ms, pulse_width_ms, duty_cycle

def update_parameters_pane(on_time_ms: int, off_time_ms: int,
                           pulse_width_ms: int, duty_cycle: float,
                           cycles: int) -> None:

    time = ((on_time_ms + off_time_ms) * cycles)
    test_UI.parameters.lines[1] = ("PW   = %s" % pretty_time(pulse_width_ms))
    test_UI.parameters.lines[2] = ("DS   = %s%%" % str(duty_cycle))
    test_UI.parameters.lines[3] = ("ON   = %s" % pretty_time(on_time_ms, 1))
    test_UI.parameters.lines[4] = ("OFF  = %s" % pretty_time(off_time_ms, 1))
    test_UI.parameters.lines[5] = ("Time = %s" % pretty_time(time, 1))
    test_UI.parameters.update_all_lines()

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


if __name__ == "cycleTest":
    gc.enable()
    gc.collect()

    print("Now starting... " + __name__)
    print("configuring hardware")

    # utime.sleep(10)
    # menu_UI.popup.pop_down()
    #

    menu_UI = MenuUI()
    # test_UI = TestUI()
    #
    # menu_UI.header.lines[2] = "SelectTest"
    # #test_UI.menu.pop_up(340,200)
#    utime.sleep(10)
#    test_UI.menu.pop_down()


#    popupActive = False

#    import tests.TEST_32109
