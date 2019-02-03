#!/bin/bash

if [ -z "$1" ]; then
    echo "Tell me where to create the tree (as first argument)"
    exit 1
fi

if [ ! -d "esp8266" ]; then
    echo "Please run this script from project's root."
    exit 1
fi

# Set dest
DEST=$1

# For each tag
git tag -l | while read TAG ; do

    # Check it out
    echo "Checking out tag $TAG" 
    git checkout $TAG

    # Create the dist tree
    mkdir -p $DEST/PythingsOS/$TAG
    cp -a * $DEST/PythingsOS/$TAG/

    # Save current folder  
    ORIGIN=$(pwd)

    # For every platform, consolidate versions and make zips
    for PLATFORM in Python MicroPython RaspberryPi esp8266 esp32 esp8266_esp-12; do
        echo "Checking if consolidate/zip $PLATFORM"
	    if [ -d "$DEST/PythingsOS/$TAG/$PLATFORM" ]; then
	        echo "Consolidating and making zip archive for \"$PLATFORM\"."
	        ZIP_LOCATION=$DEST/PythingsOS/$TAG/zips/$PLATFORM
	        mkdir -p $ZIP_LOCATION
	        cd $ZIP_LOCATION
	        rsync -r --copy-links $DEST/PythingsOS/$TAG/$PLATFORM/* ./ 
	        rm -rf __*
	        cd .. 
	        zip -r PythingsOS_${TAG}_${PLATFORM}.zip $PLATFORM
	    fi
    done
    
    # Do we have to zip the installer as well?
    echo "Checking if zip the installer for $DEST/PythingsOS/$TAG/tools/installer"
	if [ -d "$DEST/PythingsOS/$TAG/tools/installer" ]; then
	    if grep -q $TAG "$DEST/PythingsOS/$TAG/tools/installer/installer.py"; then
	    echo "Zipping the installer for \"$TAG\" in \"$ZIP_LOCATION\"."
	    ZIP_LOCATION=$DEST/PythingsOS/$TAG/zips/PythingsOS_${TAG}_installer
	    mkdir -p $ZIP_LOCATION
	    cd $ZIP_LOCATION
	    rsync -r --copy-links $DEST/PythingsOS/$TAG/tools/installer/* ./ 
	    rm -rf __*
	    cd .. 
	    zip -r PythingsOS_${TAG}_installer.zip PythingsOS_${TAG}_installer
	    fi
	fi

    # Beck to origin folder
    cd $ORIGIN

done

