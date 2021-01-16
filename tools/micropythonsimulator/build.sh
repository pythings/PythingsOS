#!/bin/bash
set -e

if [ ! -f "Dockerfile" ]; then
    # TODO: This check is WEAK: improve me!
    echo "Please run this script from the Micropython simulator root"
    exit 1
fi

# Consolidate code to be copied inside the container
rsync -avzL --exclude 'tools' --exclude 'utilities' --exclude '.git' --exclude 'artifacts' --exclude 'extras' ../../ PythingsOS

# Build the Dockerfile (and the firmware)
docker build . -t pythingsos/micropythonsimulator

# Remove the consolidated code
rm -rf PythingsOS
