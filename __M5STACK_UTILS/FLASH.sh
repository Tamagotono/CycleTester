#!/bin/sh
cd ~/Toys/ESP32/MicroPython_ESP32_psRAM_LoBo/MicroPython_BUILD/firmware/esp32_all
./flash.sh

echo "MCU is still in Bootloader mode."
echo "Please reset MCU now ..."
