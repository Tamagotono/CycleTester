

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
