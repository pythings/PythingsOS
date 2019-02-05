#!/bin/bash
set -e

# Activate virtualenv (use requirements.txt to build it)
source venv/bin/activate

if [ $# -eq 0 ]
  then
    echo "Usage: upload_os.sh serial_port os_dir"
    exit 1
fi

for i in $2/*.py; do
    [ -f "$i" ] || break
    ampy -p /dev/tty.SLAB_USBtoUART put $i
done


