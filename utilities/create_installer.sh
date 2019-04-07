#!/bin/bash

if [ ! -d "esp8266" ]; then
    echo "Please run this script from project's root."
    exit 1
fi

# Set dest
DEST='artifacts'

# Set version ref:version='v1.0.0-rc1'
VERSION=$(cat common/version.py | cut -d"'" -f2)

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










