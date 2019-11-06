#!/bin/bash

if [ ! -f "Dockerfile" ]; then
    # TODO: This check is WEAK: improve me!
    echo "Please run this script from the buildchain/espopensdk root"
    exit 1
fi

echo "Building ESP open SDK..."
docker build  -t pythings/espopensdk .
