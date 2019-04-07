#!/bin/bash

if [ ! -f "Dockerfile" ]; then
    echo "Please run this script from the buildchain root"
    exit 1
fi

echo "Copying code (for frozen firmware)..."
rsync -avz --exclude 'tools' --exclude 'utilities' --exclude '.git' --exclude 'artifacts' --exclude 'extras' ../../ PythingsOS

echo "Copying also selfarchives"
mkdir -p PythingsOS/artifacts
cp -a ../../artifacts/selfarchives PythingsOS/artifacts

echo "Building the Dokerfile and the firmware..."
docker build  -t pythingsos/buildchain .

echo "Now exporting firmware to artifacts builds folder..."
CWD=$(pwd)
docker run -v $PWD/../../artifacts/builds:/builds -i -t pythingsos/buildchain
rm -rf $PWD/../../artifacts/builds/bytecode
