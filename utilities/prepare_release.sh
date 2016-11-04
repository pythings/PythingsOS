#!/bin/bash
if [ -z "$1" ]; then
    echo "Tell me which version"
fi
echo -n "$1" > version
rm -f files.txt
python utilities/create_files_list.py > files.txt
python utilities/create_files_list.py > /tmp/pythings_files.txt
mv /tmp/pythings_files.txt files.txt
python utilities/create_files_list.py > /tmp/pythings_files.txt
mv /tmp/pythings_files.txt files.txt

