#!/bin/bash
while true; do
    python3 boot.py
    read -t 3 -p "Rebooting Pythings OS in 3 seconds... (type \"q\" [enter] to stop the reboot and quit) " yn
    case $yn in
        [Qq]* ) exit;;
        * ) "Pythings OS reboot will continue";;
    esac
done
