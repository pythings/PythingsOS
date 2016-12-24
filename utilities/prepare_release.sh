#!/bin/bash
if [ -z "$1" ]; then
    echo "Tell me which version!! (i.e. utilities/prepare_release.sh v0.1)"
    exit 1
fi

echo "version='$1'" > common/version.py

architectures=( 'MicroPython' 'esp8266' 'esp8266_esp-12' )
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

# Create installers
python utilities/create_installer.py
