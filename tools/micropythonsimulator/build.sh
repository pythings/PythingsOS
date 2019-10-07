#!/bin/bash

if [ ! -f "Dockerfile" ]; then
    # TODO: This check is WEAK: improve me!
    echo "Please run this script from the Micropython simulator root"
    exit 1
fi

#echo "Copying code ..."
#rsync -avz --exclude 'tools' --exclude 'utilities' --exclude '.git' --exclude 'artifacts' --exclude 'extras' ../../ PythingsOS

echo "Building the Dokerfile and the firmware..."
docker build . -t pythingsos/micropythonsimulator





