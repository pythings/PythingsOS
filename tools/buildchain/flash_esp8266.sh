#!/bin/bash

if [ $# -eq 0 ]
  then
    echo "Usage: flash_esp8266.sh serial_port firmware_file"
    exit 1
fi


esptool.py --port $1 erase_flash
sleep 5
esptool.py --port $1 --baud 115200 write_flash --flash_size=detect -fm dio 0 $2
