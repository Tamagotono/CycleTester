
def M5stack():
    import lib.m5stack as m5stack
    import display
    import machine

    tft = display.TFT()
    tft = m5stack.Display(40000000)

    machine.freq(240000000)

    m5stack.tone(1, duration=0, volume=0)  # Prevents first tone being at full volume

    def button_hander_a(pin, pressed):
        if pressed is True:
            tft.text(
                tft.CENTER, tft.LASTY, "> Button A pressed.     "
            )
            m5stack.tone(1800, duration=10, volume=1)
        else:
            tft.text(
                tft.CENTER, tft.LASTY, "> Button A released.    "
            )
            m5stack.tone(1300, duration=10, volume=1)

    def button_hander_b(pin, pressed):
        if pressed is True:
            tft.text(
                tft.CENTER, tft.LASTY, "> Button B pressed.     "
            )
            m5stack.tone(2000, duration=10, volume=1)
        else:
            tft.text(
                tft.CENTER, tft.LASTY, "> Button B released.    "
            )
            m5stack.tone(1500, duration=10, volume=1)

    def button_hander_c(pin, pressed):
        if pressed is True:
            tft.text(
                tft.CENTER, tft.LASTY, "> Button C pressed.     "
            )
            m5stack.tone(2200, duration=10, volume=1)
        else:
            tft.text(
                tft.CENTER, tft.LASTY, "> Button C released.    "
            )
            m5stack.tone(1800, duration=10, volume=1)

    return tft
           # m5stack.ButtonA(callback=button_hander_a),\
           # m5stack.ButtonB(callback=button_hander_b),\
           # m5stack.ButtonC(callback=button_hander_c)

def ESP32_WROVER_KIT_v3():
    import display
    tft = display.TFT()
    tft.init(tft.ST7789, rst_pin=18, backl_pin=5, miso=25, mosi=23, clk=19, cs=22, dc=21)
    return tft

def Adafruit_TFT_FeatherWing():
    import display
    tft = display.TFT()
    tft.init(tft.ILI9341, width=240, height=320, miso=19, mosi=18, clk=5, cs=15, dc=33, bgr=True, hastouch=tft.TOUCH_STMPE, tcs=32)
    return tft

def generic_ILI9341():
    import display
    tft = display.TFT()
    tft.init(tft.ILI9341, width=240, height=320, miso=19,mosi=23,clk=18,cs=5,dc=26,tcs=27,hastouch=True, bgr=True)
    return tft

def generic_ST7735R():
    import display
    tft = display.TFT()
    tft.init(tft.ST7735R, speed=10000000, spihost=tft.HSPI, mosi=13, miso=12, clk=14, cs=15, dc=27, rst_pin=26, hastouch=False, bgr=False, width=128, height=160)
    return tft
