#!/bin/bash

if [ ! -f "Dockerfile" ]; then
    echo "Please run this script from the buildchain root"
    exit 1
fi

PWD_OR=$(pwd)
echo "Generating installers (for non-frozen firmware)..."

cd ..
cd ..
python utilities/create_installers.py

cd $PWD_OR

echo "Copying code (for frozen firmware)..."
rsync -avz --exclude 'tools' --exclude 'utilities' --exclude '.git' --exclude 'builds' --exclude 'extras' ../../ PythingsOS

echo "Building the Dokerfile and the firmware..."
docker build  -t pythingsos/buildchain .

echo "Now exporting firmware to builds folder..."
CWD=$(pwd)
docker run -v $PWD/../../builds:/builds -i -t pythingsos/buildchain
rm -rf $PWD/../../builds/bytecode
