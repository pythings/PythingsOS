#!/bin/bash

if [ ! -d "esp8266" ]; then
    echo "Please run this script from project's root."
    exit 1
fi

VERSION=$(cat tools/buildchain/Dockerfile | grep "ENV VER" | cut -d'"' -f2)

echo "I will finalize version $VERSION"




