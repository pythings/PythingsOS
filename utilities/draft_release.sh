#!/bin/bash
if [ -z "$1" ]; then
    echo "Tell me which version!! (i.e. utilities/draft_release.sh v1.0.0)"
    exit 1
fi

if [ ! -d "esp8266" ]; then
    echo "Please run this script from project's root."
    exit 1
fi

VERSION=$1

echo ""

# 1) Update versions
echo "Updating versions..."
echo "version='$VERSION'" > common/version.py

OLD_VER_LINE=$(cat tools/buildchain/Dockerfile | grep "ENV VER")
NEW_VER_LINE="ENV VER=\"$VERSION\""
sed -i'' -e "s/$OLD_VER_LINE/$NEW_VER_LINE/g" tools/buildchain/Dockerfile
rm -f tools/buildchain/Dockerfile-e

echo "OK"
echo ""


# 2) Create file lists
echo "Creating file lists..."
platforms=( 'MicroPython' 'esp8266' 'esp8266_esp-12' 'Python' 'esp32' 'RaspberryPi')
for dir in "${platforms[@]}"
do
    echo " $dir"
    cd $dir
    rm -f files.txt
    python ../utilities/create_files_list.py > files.txt
    python ../utilities/create_files_list.py > /tmp/pythings_files.txt
    mv /tmp/pythings_files.txt files.txt
    python ../utilities/create_files_list.py > /tmp/pythings_files.txt
    mv /tmp/pythings_files.txt files.txt
    cd ..
done
echo "OK"
echo ""


# 3) Create the installer 
echo "Creating the installer..."

utilities/create_installer.sh artifacts > /dev/null

echo "OK"
echo ""


# 4) Create the zips 
echo "Creating zips..."

utilities/create_zips.sh > /dev/null

echo "OK"
echo ""


# 5) Create the self-extracting archives for the firmwares
echo "Creating the self-extracting archives..."
python utilities/create_selfarchives.py

echo "OK"
echo ""


# 6) Build the firmwares (standard using the selfarchvies and frozen using the coeebase)
echo "Building the firmwares..."

cd tools/buildchain
./build.sh #> /dev/null
cd ..
cd ..
echo "OK"
echo ""


# 7) Cleanup
echo "Cleanup..."

rm -rf artifacts/selfarchives
echo "OK"
echo ""





