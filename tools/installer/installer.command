#!/bin/bash

here="`dirname \"$0\"`"
#echo "Moving to $here"
cd $here
clear

if [ -z "$PYTHON" ]; then
    PYTHON='python'
fi

$PYTHON installer.py

