#!/bin/bash

if [ "$1" == "bash" ]; then
    bash
else
    cp -a /home/xtensa/builds/* /firmware
fi

