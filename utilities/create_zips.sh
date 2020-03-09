#!/bin/bash

if [ ! -d "esp8266" ]; then
    echo "Please run this script from project's root."
    exit 1
fi

VERSION=$(cat tools/buildchain/Dockerfile | grep "ENV VER" | cut -d'"' -f2)

# Set tmp dir
EPOCH_NOW=$(date +'%s')
TMP_DIR=/tmp/PythingsOS_$EPOCH_NOW

mkdir -p artifacts/zips

# For each tag? (old behavior, deprecated)
FOR_EACH_TAG=false
if [ "$FOR_EACH_TAG" = true ]; then
    git tag -l | while read TAG ; do
    
        # Check it out
        echo "Checking out tag $TAG" 
        git checkout $TAG
    
        # Create the dist tree
        mkdir -p $TMP_DIR/PythingsOS/$TAG
        cp -a * $TMP_DIR/PythingsOS/$TAG/
    
        # Save current folder  
        ORIGIN=$(pwd)
    
        # For every platform, consolidate versions and make zips
        for PLATFORM in Python MicroPython RaspberryPi esp8266 esp32 esp8266_sim800 esp32_sim800; do
            # TODO: include the logic below
            :
        done
    


    done
    echo "Placed zips in $TMP_DIR"
else

    # Save current folder  
    ORIGIN=$(pwd)

    # For every platform, consolidate versions and make zips
    for PLATFORM in Python MicroPython RaspberryPi esp8266 esp32 esp8266_sim800 esp32_sim800; do
        echo "Consolidating and making zip archive for \"$PLATFORM\"."
        ZIP_LOCATION=$TMP_DIR/$VERSION/zips/$PLATFORM
        mkdir -p $ZIP_LOCATION
        cd $ZIP_LOCATION
        rsync -r --copy-links $ORIGIN/$PLATFORM/* ./ 
        rm -rf __*
        cd ..
        zip -r PythingsOS_${VERSION}_${PLATFORM}.zip $PLATFORM
        mv PythingsOS_${VERSION}_${PLATFORM}.zip $ORIGIN/artifacts/zips/
        # Back to origin folder
        cd $ORIGIN
    done

fi

# Remove temp dir
rm -rf $TMP_DIR
