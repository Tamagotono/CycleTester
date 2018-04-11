

#import machine, display, time,
import machine, _thread, math
#import m5stack
import utime, machine #Cycle count required imports
from micropython import const
import hardware_config
import gc

tft, btn_a, btn_b, btn_c = hardware_config.M5stack()

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

    time=str("%1dy %1dw %1dd" % (years, weeks, days))
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
    gc.collect()

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

    def __init__(self):
        tft.clear()
        self.screenwidth, self.screenheight = tft.screensize()
        self.header = self.DisplaySection(0,0,40, self.screenwidth)
        self.prameters = self.DisplaySection(0,41,120, self.screenwidth, fill_color=tft.GREEN)
#        self.status = self.DisplaySection(0,121,60, self.screenwidth)

    class DisplaySection:
        def __init__(self,
                     x:int,
                     y:int,
                     frame_height:int,
                     frame_width:int,
                     frame_color:int = tft.WHITE,
                     fill_color:int = tft.BLUE,
                     text_color:int = tft.WHITE,
                     font = tft.FONT_DejaVu18,
                    ):

            self.x = x
            self.y = y
            self.frame_width = frame_width
            self.frame_height = frame_height
            self.frame_color = frame_color
            self.fill_color = fill_color
            self.text_color = text_color
            self.font = font
            tft.font(self.font)
            self.frame_height = 40
            self.line_height, self.text_y = self.line_height_margin_calc(10)
            self.num_of_lines = int(self.frame_height / self.line_height)
            self.lines = {}

            tft.set_bg(self.fill_color)
            tft.set_fg(self.text_color)

            self.create_lines(self.num_of_lines)
            self.initialize_section()

        def initialize_section(self):
            tft.font(self.font)
            tft.rect(self.x, self.y, self.frame_width, self.frame_height, self.frame_color, self.fill_color)
            self.create_lines(self.num_of_lines)
            self.update_all_lines()


        def line_height_margin_calc(self, margin:int = 10) -> int:
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
            print("line_height_margin_calc: line_height_px = " + str(line_height_px) + 'margin:' + str(margin/2))
            return line_height_px, int(margin_px/2)

        def create_lines(self, num_of_lines:int):
            """
            Args:
                num_of_lines (int): initializes the dictionary of the text for each line number
            Returns:
                Nothing
            """
            line_num = 1
            while line_num <= num_of_lines:
                self.lines[line_num] = str(line_num)
                line_num += 1
            print(self.lines.items())

        def update_line(self, line_number:int):
            """
            Args:
                line_number (int): The line number to update on the desplay
            Returns:
                Nothing
            """
            line_y = ((line_number - 1) * self.line_height)
            text_y = line_y + self.text_y
            tft.rect(self.x, line_y, self.frame_width, self.line_height, self.fill_color, self.fill_color)
            tft.text(self.x, text_y, self.lines.get(line_number, "ERROR"),
                     self.text_color, transparent=True)

        def update_all_lines(self):
            """
            Returns:
                Nothing
            Notes:
                Quick way to update all lines in the section
            """
            line_num = 1
            while line_num <= self.num_of_lines:
                self.update_line(line_num)
                line_num += 1




    # def header(self):
    #     FRAME_COLOR = tft.BLUE
    #     FILL_COLOR = tft.BLUE
    #     TEXT_COLOR = 0xffffff
    #     HEIGHT = 40
    #     LINE1_Y = 0
    #     LINE2_Y = 20
    #
    #     tft.rect(0, 0, 320, HEIGHT, FRAME_COLOR, FILL_COLOR)
    #     tft.textClear(tft.CENTER,LINE1_Y, self.h1_text)
    #     tft.text(tft.CENTER,LINE1_Y, self.h1_text, TEXT_COLOR, transparent=True)
    #     tft.textClear(tft.CENTER,LINE2_Y, self.h2_text)
    #     tft.text(tft.CENTER,LINE2_Y, self.h2_text, TEXT_COLOR, transparent=True)
    #
    # def test_param(self):
    #     FRAME_COLOR = tft.BLUE
    #     FILL_COLOR = tft.BLUE
    #     TEXT_COLOR = 0xffffff
    #     HEIGHT = 60
    #     text_line_1 = ''
    #     text_line_2 = ''
    #
    #     tft.rect(0, 0, 320, 20, tft.RED, tft.RED)
    #     #printLCD(TEST_NAME_1, Y=LCDTitle1, Background=BLACK)
    #     #printLCD(TEST_NAME_2, Y=LCDTitle2, Background=BLACK)
    #
    # def test_status(self):
    #     FRAME_COLOR = tft.BLUE
    #     FILL_COLOR = tft.BLUE
    #     TEXT_COLOR = 0xffffff
    #     HEIGHT = 60
    #     #text_line_1 = ''
    #     #text_line_2 = ''
    #
    #     tft.rect(0, 0, 320, 20, tft.RED, tft.RED)
    #     printLCD(TEST_NAME_1, Y=LCDTitle1, Background=BLUE)
    #     printLCD(TEST_NAME_2, Y=LCDTitle2, Background=BLUE)

    def footer(self):
        tft.rect( 25, 210, 80, 30, tft.RED, tft.BLUE)
        tft.text( 50, 215,   "UP", tft.WHITE, transparent=True)

        tft.rect(120, 210, 80, 30, tft.RED, tft.BLUE)
        tft.text(120, 215, "DOWN", tft.WHITE, transparent=True)

        tft.rect(215, 210, 80, 30, tft.RED, tft.BLUE)
        tft.text(235, 215,  "SEL", tft.WHITE, transparent=True)

    def printLCD(text, X=0, Y=0, bg_color=0x000000, text_color=0xffffff, transparent=True):
        text = str(text)
        tft.textClear(X, Y, text)
        tft.text(X, Y, text, text_color, transparent=True)
