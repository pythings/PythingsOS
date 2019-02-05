#!/bin/bash
if [ -z "$1" ]; then
    echo "Tell me which version!! (i.e. utilities/prepare_release.sh v0.1)"
    exit 1
fi

echo "version='$1'" > common/version.py

echo "VER='$1'" > tools/buildchain/ver.sh

if [ ! -d "esp8266" ]; then
    echo "Please run this script from project's root."
    exit 1
fi

architectures=( 'MicroPython' 'esp8266' 'esp8266_esp-12' 'Python')
for dir in "${architectures[@]}"
do
    echo $dir
    cd $dir
    rm -f files.txt
    python ../utilities/create_files_list.py > files.txt
    python ../utilities/create_files_list.py > /tmp/pythings_files.txt
    mv /tmp/pythings_files.txt files.txt
    python ../utilities/create_files_list.py > /tmp/pythings_files.txt
    mv /tmp/pythings_files.txt files.txt
    cd ..
done

echo ""
echo "OK, now change the VER env var in the tools/buildchain/Dockerfile as well."
echo ""