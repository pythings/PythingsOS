#!/bin/bash
set -e

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

# 0) Clean previous artifacts
rm -rf artifacts

# 0.1) Download a clean esp32 firmware
mkdir -p artifacts/firmware
OR_DIR=$PWD
cd artifacts/firmware && wget http://pythings.io/static/MicroPython/esp32-20190529-v1.11.bin
cd $OR_DIR

# 1) Update versions
echo "Updating versions..."
echo "version='$VERSION'" > common/version.py

# In the buildchain..
OLD_VER_LINE=$(cat tools/buildchain/Dockerfile | grep "ENV VER")
NEW_VER_LINE="ENV VER=\"$VERSION\""
sed -i'' -e "s/$OLD_VER_LINE/$NEW_VER_LINE/g" tools/buildchain/Dockerfile
rm -f tools/buildchain/Dockerfile-e

# In the installer..
OLD_VER_LINE=$(cat tools/installer/installer.py | grep "DEFAULT_VERSION" | head -n1)
NEW_VER_LINE="DEFAULT_VERSION          = '$VERSION'"
sed -i'' -e "s/$OLD_VER_LINE/$NEW_VER_LINE/g" tools/installer/installer.py
rm -f tools/installer/installer.py-e
echo "OK"
echo ""


# 2) Create file lists
echo "Creating file lists..."
platforms=( 'MicroPython' 'esp8266' 'esp8266_sim800' 'Python' 'esp32' 'RaspberryPi' 'esp32_sim800')
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


# 3) Create the zips 
echo "Creating zips..."

utilities/create_zips.sh > /dev/null

echo "OK"
echo ""


# 4) Create the self-extracting archives for the firmwares
echo "Creating the self-extracting archives..."
python utilities/create_selfarchives.py

echo "OK"
echo ""


# 5) Build the firmwares (standard using the selfarchvies and frozen using the coeebase)
echo "Building the firmwares..."

cd tools/buildchain
./build.sh #> /dev/null
cd ..
cd ..
echo "OK"
echo ""


# 6) Create the installer 
echo "Creating the installer..."

utilities/create_installer.sh artifacts > /dev/null

echo "OK"
echo ""


# 7) Cleanup
echo "Cleanup..."

rm -rf artifacts/selfarchives
echo "OK"
echo ""





