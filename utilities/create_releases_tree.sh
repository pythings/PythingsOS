#!/bin/bash

if [ -z "$1" ]; then
    echo "Tell me where to create the tree (as first argument)"
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
    for PLATFORM in Python MicroPython RaspberryPi; do   
	    if [ -d "$DEST/PythingsOS/$TAG/$PLATFORM" ]; then
	        echo "Consolidating and making zip archive for \"$PLATFORM\"."
	        ZIP_LOCATION=$DEST/PythingsOS/$TAG/zips
	        mkdir -p $ZIP_LOCATION
	        cd $ZIP_LOCATION
	        rsync -r --copy-links $DEST/PythingsOS/$TAG/$PLATFORM/* ./ 
	        rm -rf __*
	        cd .. 
	        zip -r PythingsOS_${TAG}_${PLATFORM}.zip $PLATFORM
	    fi
    done

    # Beck to origin folder
    cd $ORIGIN

done

