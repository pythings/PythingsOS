#!/bin/bash
esptool.py --port /dev/cu.wchusbserial1420 erase_flash
sleep 5
esptool.py --port /dev/cu.wchusbserial1420 --baud 115200 write_flash --flash_size=detect -fm dio 0 esp8266-20180511-v1.9.4.bin #esp8266-20180718-v1.9.4-272-g46091b8a.bin #PythingsOS_v0.1__uPy_v1.8.6-94-gf8b71aa.esp8266_esp-12.bin 
