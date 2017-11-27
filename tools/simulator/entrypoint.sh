#!/bin/bash


if [ "$1" == "bash" ]; then
  bash
  exit 0
fi

if [ "$1" == "micropython" ]; then
    /micropython/unix/micropython
    exit 0
fi


aid="$1"
tid="$2"

if [ -z "${aid}" ]; then
    echo "Usage: docker run -i -t pythings/simulator AID TID"
    echo "       docker run -i -t pythings/simulator micropython"
    echo "       docker run -i -t pythings/simulator bash"
    exit 1
fi

if [ -z "${tid}" ]; then
    echo "Usage: docker run -i -t pythings/simulator AID TID"
    echo "       docker run -i -t pythings/simulator micropython"
    echo "       docker run -i -t pythings/simulator bash"
    exit 1
fi

echo -n "$aid" > /opt/PythingsOS/builds/MicroPython/aid

if [ ! -z "${tid}" ]; then
    echo -n "$tid" > /opt/PythingsOS/builds/MicroPython/tid
fi

cd /opt/PythingsOS/builds/MicroPython
while true; do
    ./run.sh
    read -t 3 -p "Rebooting PythingsOS in 3 seconds... (otherwise type \"q\" [enter] to quit, \"s\" [enter] for a shell) " yn
    case $yn in
        [Qq]* ) exit;;
        [Ss]* ) bash;;
        * ) echo "Please answer x or b";;
    esac
done


