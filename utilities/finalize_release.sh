#!/bin/bash

if [ ! -d "esp8266" ]; then
    echo "Please run this script from project's root."
    exit 1
fi

VERSION=$(cat tools/buildchain/Dockerfile | grep "ENV VER" | cut -d'"' -f2)

PYTHINGSDATA_DIR="../PythingsData"

if [ ! -d "$PYTHINGSDATA_DIR" ]; then
    echo "Error, no PythingsData dir found"
    exit 1
fi

echo ""
echo "I will finalize version $VERSION, and commit everything listed below:"
echo ""

git status

echo ""
echo "Again, I will commit EVERYTHING marked in red above, for version $VERSION."
read -p "Are you sure? [y/n]" -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Ok, proceeding"

    # 1) Create a commit and tag for PythingsOS repo
    git add *
    git commit -m "Release $VERSION"
    git tag -a v1.0.1
    git push origin v1.0.1
    git push

    # 2) Copy artifacts: zips, installer, firmware
    copy -a artifacts/installer/* $PYTHINGSDATA_DIR/PythingsOS/installer/
    copy -a artifacts/zips/* $PYTHINGSDATA_DIR/PythingsOS/zips/
    copy -a artifacts/firmware/* $PYTHINGSDATA_DIR/PythingsOS/firmware/

    # 3) Create a commit for PythingsData repo
    cd $PYTHINGSDATA_DIR
    git add PythingsOS/
    git commit -m "Added PythingsOS files for $VERSION"
    git push
    HASH=$(git rev-parse HEAD)
    echo "PythingsData commit to include in PythingsCloud: $HASH"
    exit 0
fi

exit 0


