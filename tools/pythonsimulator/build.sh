#!/bin/bash
set -e

if [ ! -f "Dockerfile" ]; then
    # TODO: This check is WEAK: improve me!
    echo "Please run this script from the Python simulator root"
    exit 1
fi

# Consolidate code to be copied inside the container
rsync -avzL --exclude 'tools' --exclude 'utilities' --exclude '.git' --exclude 'artifacts' --exclude 'extras' ../../ PythingsOS

# Build the Dockerfile 
docker build . -t pythingsos/pythonsimulator

# Remove the consolidated code
rm -rf PythingsOS
