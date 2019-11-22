#!/bin/bash

if [ ! -d "esp8266" ]; then
    echo "Please run this script from project's root."
    exit 1
fi

# Set dest
DEST='artifacts/installer'

# Set version from version.py, expected content: "version='...'"
VERSION=$(cat common/version.py | cut -d"'" -f2)

# Clean installer artifacts
rm -rf tools/installer/artifacts

# Copy new installer artifacts opy artifacts
cp -a artifacts tools/installer/artifacts

echo "Creating the installer as version $VERSION in $DEST.."
if [ -d "tools/installer" ]; then
    ZIP_LOCATION=$DEST/PythingsOS_${VERSION}_installer
    mkdir -p $ZIP_LOCATION
    
    # Save current folder  
    ORIGIN=$(pwd)
    
    cd $ZIP_LOCATION
    rsync -r --copy-links $ORIGIN/tools/installer/* ./ 
    rm -rf __*
    cd .. 
    zip -r PythingsOS_${VERSION}_installer.zip PythingsOS_${VERSION}_installer
    rm -rf PythingsOS_${VERSION}_installer
    # Back to origin
    cd $ORIGIN

else

    echo "Error, could not find the installer dir?"
    exit 1

fi










