#!/bin/bash


if [ "$1" == "bash" ]; then
  bash
  exit 0
fi

aid="$1"
tid="$2"
be="$3"

if [ -z "${aid}" ]; then
    echo "Usage: docker run -i -t pythingsos/pythonsimulator AID TID (BACKEND)"
    echo "       docker run -i -t pythingsos/pythonsimulator bash"
    exit 1
fi

if [ -z "${tid}" ]; then
    echo "Usage: docker run -i -t pythingsos/pythonsimulator AID TID (BACKEND)"
    echo "       docker run -i -t pythingsos/pythonsimulator bash"
    exit 1
fi

if [ -z "${be}" ]; then
    echo "Using default backend"
else
    echo "Using backend: \"$be\""
    echo -n "$be" > $HOME/.pythings/backend
fi

echo -n "$aid" > $HOME/.pythings/aid

if [ ! -z "${tid}" ]; then
    echo -n "$tid" > $HOME/.pythings/tid
fi

# Move to the right path
cd /opt/PythingsOS/MicroPython

while true; do
    
    micropython boot.py &> /tmp/logs/PythingsOS.log

    read -t 3 -p "Rebooting Pythings OS in 3 seconds... (otherwise type \"q\" [enter] to quit, \"s\" [enter] for a shell) " yn
    case $yn in
        [Qq]* ) exit;;
        [Ss]* ) bash;;
        * ) echo "Please answer q or s";;
    esac
done

