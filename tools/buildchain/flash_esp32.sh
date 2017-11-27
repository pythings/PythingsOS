#!/bin/bash
#/dev/tty.SLAB_USBtoUART
if [ $# -eq 0 ]
  then
    echo "Usage: flash_esp32.sh serial_port firmware_file"
    exit 1
fi


#esptool.py --port $1 erase_flash
#sleep 5
esptool.py --chip esp32 --port $1 write_flash -z 0x1000 $2
