#!/bin/bash

if [ -z "$1" ]; then
    echo "Tell me where t create the tree (as first argument)"
    exit 1
fi

# Set dest
DEST=$1

# Get tags from Git
git tag -l | while read TAG ; do

# For each tag
echo "Checking out tag $TAG" 
git checkout $TAG

mkdir -p $DEST/PythingsOS/$TAG
cp -a * $DEST/PythingsOS/$TAG/
  
done

