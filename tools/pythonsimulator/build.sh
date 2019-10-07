#!/bin/bash

if [ ! -f "Dockerfile" ]; then
    # TODO: This check is WEAK: improve me!
    echo "Please run this script from the Python simulator root"
    exit 1
fi

docker build . -t pythingsos/pythonsimulator

